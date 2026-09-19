# -*- coding: utf-8 -*-
"""
Rubrol Stripe Fulfillment & License Key Provisioning Webhook.
Listens for checkout.session.completed events, extracts the GitHub username
from checkout custom_fields, issues a signed 1-year offline cryptographic license key,
and automatically invites the customer to private GitHub vaults:
- Pro Sidecar: maxcomperatore/rubrol-pro-vault
- EU Enterprise: maxcomperatore/rubrol-pro-vault + maxcomperatore/rubrol-enterprise-vault
"""
import os
import sys
import json
import logging
import urllib.request
import urllib.error
import subprocess
from typing import Optional, Dict, Any, List

from rubrol.core.api_key_manager import key_manager
from rubrol.core.license import generate_license_key, verify_license_key

logger = logging.getLogger("rubrol.webhooks.stripe")

VAULT_OWNER = os.environ.get("RUBROL_VAULT_OWNER", "maxcomperatore")
PRO_VAULT_REPO = os.environ.get("RUBROL_PRO_VAULT_REPO", "rubrol-pro-vault")
ENTERPRISE_VAULT_REPO = os.environ.get("RUBROL_ENTERPRISE_VAULT_REPO", "rubrol-enterprise-vault")


def get_github_token() -> Optional[str]:
    """Retrieve GitHub token from environment or local gh CLI auth."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    try:
        res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, shell=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception as e:
        logger.warning(f"Failed to obtain token from gh CLI: {e}")
    return None


def invite_github_user_to_repo(github_username: str, repo_name: str, permission: str = "pull") -> Dict[str, Any]:
    """
    Send an invitation to the given GitHub username for a private Rubrol repository.
    """
    clean_username = github_username.strip().lstrip("@")
    if not clean_username:
        return {"success": False, "error": "Empty GitHub username provided"}

    token = get_github_token()
    if not token:
        logger.error("Cannot invite user: No GITHUB_TOKEN or gh CLI authentication found.")
        return {"success": False, "error": "No GitHub token available"}

    full_repo = f"{VAULT_OWNER}/{repo_name}"
    url = f"https://api.github.com/repos/{full_repo}/collaborators/{clean_username}"
    payload = json.dumps({"permission": permission}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "Rubrol-Fulfillment-Bot"
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8")) if resp.length else {}
            logger.info(f"Successfully invited @{clean_username} to {full_repo} (HTTP {resp.status})")
            return {
                "success": True,
                "status": resp.status,
                "username": clean_username,
                "repository": full_repo,
                "response": resp_data
            }
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8") if hasattr(err, "read") else str(err)
        logger.error(f"GitHub API error inviting @{clean_username} to {full_repo}: HTTP {err.code} - {err_msg}")
        return {"success": False, "status": err.code, "error": err_msg, "repository": full_repo, "username": clean_username}
    except Exception as exc:
        logger.error(f"Unexpected error inviting @{clean_username} to {full_repo}: {exc}")
        return {"success": False, "error": str(exc), "repository": full_repo, "username": clean_username}


def process_stripe_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an incoming Stripe webhook event.
    """
    event_type = event.get("type", "")
    logger.info(f"Processing Stripe webhook event: {event_type} (id: {event.get('id')})")

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        customer_details = session.get("customer_details", {})
        email = customer_details.get("email", "unknown")
        name = customer_details.get("name", "Customer")

        # 1. Extract GitHub username from custom fields or metadata
        github_username = None
        custom_fields = session.get("custom_fields", [])
        for field in custom_fields:
            if field.get("key") in ("github_username", "github"):
                github_username = field.get("text", {}).get("value", "").strip()
                break

        if not github_username:
            github_username = session.get("metadata", {}).get("github_username") or session.get("client_reference_id")

        # 2. Determine license tier
        amount_total = session.get("amount_total", 0)  # In cents
        raw_tier = session.get("metadata", {}).get("tier", "").lower()
        
        if "enterprise" in raw_tier or "compliance" in raw_tier or amount_total >= 400000:
            tier = "eu_enterprise"
            target_repos = [PRO_VAULT_REPO, ENTERPRISE_VAULT_REPO]
        else:
            tier = "pro_sidecar"
            target_repos = [PRO_VAULT_REPO]

        # 3. Generate Cryptographic 1-Year Offline License Key
        license_key = generate_license_key(
            customer_email=email,
            github_username=github_username or "unspecified",
            tier=tier,
            valid_days=365
        )
        logger.info(f"Generated 1-year {tier} license key for {email}: {license_key[:35]}...")

        # 4. Provision API key in local DB (backward compatibility)
        customer_id = session.get("customer", "")
        subscription_id = session.get("subscription", "")
        api_key_info = {}
        if email and email != "unknown":
            try:
                api_key_info = key_manager.provision_paid_key(
                    email=email,
                    tier=tier,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id
                )
            except Exception as ex:
                logger.error(f"Failed to provision API key for {email}: {ex}")

        # 5. Invite to GitHub Vaults if GitHub username was provided
        invite_results: List[Dict[str, Any]] = []
        if github_username:
            for repo in target_repos:
                res = invite_github_user_to_repo(github_username, repo)
                invite_results.append(res)

        return {
            "handled": True,
            "event_type": event_type,
            "customer_email": email,
            "customer_name": name,
            "tier": tier,
            "github_username": github_username,
            "license_key": license_key,
            "api_key_info": api_key_info,
            "vault_invitations": invite_results
        }

    return {"handled": False, "event_type": event_type, "message": "Event type not requiring fulfillment"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if "--test-invite" in sys.argv:
        idx = sys.argv.index("--test-invite")
        if idx + 1 < len(sys.argv):
            target_user = sys.argv[idx + 1]
            repo = sys.argv[idx + 2] if idx + 2 < len(sys.argv) else PRO_VAULT_REPO
            print(f"Testing GitHub invitation for @{target_user} to {repo}...")
            res = invite_github_user_to_repo(target_user, repo)
            print("Result:", json.dumps(res, indent=2))
        else:
            print("Usage: python -m rubrol.webhooks.stripe_fulfillment --test-invite <username> [repo_name]")
    elif "--listen" in sys.argv:
        print("Starting Stripe webhook listener forwarding to localhost:8080/api/webhooks/stripe...")
        subprocess.run(["stripe", "listen", "--forward-to", "localhost:8080/api/webhooks/stripe"], shell=True)
    else:
        print("Rubrol Stripe Fulfillment & License Key Module.")
        print("Commands:")
        print("  python -m rubrol.webhooks.stripe_fulfillment --test-invite <username> [repo_name]")
        print("  python -m rubrol.webhooks.stripe_fulfillment --listen")
