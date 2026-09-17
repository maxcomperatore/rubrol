# -*- coding: utf-8 -*-
"""
Rubrol Stripe Fulfillment Webhook
Listens for checkout.session.completed events, extracts the GitHub username
from the checkout custom_fields, and automatically invites the customer
to the private maxcomperatore/rubrol-pro-vault repository.
"""
import os
import sys
import json
import logging
import urllib.request
import urllib.error
import subprocess
from typing import Optional, Dict, Any

logger = logging.getLogger("rubrol.webhooks.stripe")

VAULT_REPO_OWNER = os.environ.get("RUBROL_VAULT_OWNER", "maxcomperatore")
VAULT_REPO_NAME = os.environ.get("RUBROL_VAULT_REPO", "rubrol-pro-vault")

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

def invite_github_user_to_vault(github_username: str, permission: str = "pull") -> Dict[str, Any]:
    """
    Send an invitation to the given GitHub username for the private Rubrol Pro Vault.
    """
    clean_username = github_username.strip().lstrip("@")
    if not clean_username:
        return {"success": False, "error": "Empty GitHub username provided"}

    token = get_github_token()
    if not token:
        logger.error("Cannot invite user: No GITHUB_TOKEN or gh CLI authentication found.")
        return {"success": False, "error": "No GitHub token available"}

    url = f"https://api.github.com/repos/{VAULT_REPO_OWNER}/{VAULT_REPO_NAME}/collaborators/{clean_username}"
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
            logger.info(f"Successfully invited @{clean_username} to {VAULT_REPO_OWNER}/{VAULT_REPO_NAME} (HTTP {resp.status})")
            return {
                "success": True,
                "status": resp.status,
                "username": clean_username,
                "repository": f"{VAULT_REPO_OWNER}/{VAULT_REPO_NAME}",
                "response": resp_data
            }
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8") if hasattr(err, 'read') else str(err)
        logger.error(f"GitHub API error inviting @{clean_username}: HTTP {err.code} - {err_msg}")
        return {"success": False, "status": err.code, "error": err_msg, "username": clean_username}
    except Exception as exc:
        logger.error(f"Unexpected error inviting @{clean_username}: {exc}")
        return {"success": False, "error": str(exc), "username": clean_username}

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

        # Extract GitHub username from custom fields
        github_username = None
        custom_fields = session.get("custom_fields", [])
        for field in custom_fields:
            if field.get("key") == "github_username":
                github_username = field.get("text", {}).get("value", "").strip()
                break

        if not github_username:
            github_username = session.get("metadata", {}).get("github_username")

        if github_username:
            invite_res = invite_github_user_to_vault(github_username)
            return {
                "handled": True,
                "event_type": event_type,
                "customer_email": email,
                "customer_name": name,
                "github_username": github_username,
                "invitation": invite_res
            }
        else:
            logger.warning(f"Checkout session {session.get('id')} completed without GitHub username.")
            return {
                "handled": True,
                "event_type": event_type,
                "warning": "No GitHub username found in checkout session",
                "customer_email": email
            }

    return {"handled": False, "event_type": event_type, "message": "Event type not requiring fulfillment"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if "--test-invite" in sys.argv:
        idx = sys.argv.index("--test-invite")
        if idx + 1 < len(sys.argv):
            target_user = sys.argv[idx + 1]
            print(f"Testing GitHub invitation for user: {target_user}")
            res = invite_github_user_to_vault(target_user)
            print("Result:", json.dumps(res, indent=2))
        else:
            print("Usage: python -m rubrol.webhooks.stripe_fulfillment --test-invite <username>")
    elif "--listen" in sys.argv:
        print("Starting Stripe webhook listener forwarding to localhost:8080/api/webhooks/stripe...")
        subprocess.run(["stripe", "listen", "--forward-to", "localhost:8080/api/webhooks/stripe"], shell=True)
    else:
        print("Rubrol Stripe Fulfillment Module.")
        print("Commands:")
        print("  python -m rubrol.webhooks.stripe_fulfillment --test-invite <username>")
        print("  python -m rubrol.webhooks.stripe_fulfillment --listen")
