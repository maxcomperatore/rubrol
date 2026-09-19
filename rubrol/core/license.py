# -*- coding: utf-8 -*-
"""
Rubrol Cryptographic Offline License Key System.
Enables air-gapped, zero-outbound-network license validation for enterprise sidecars.
Uses HMAC-SHA256 signatures with payload integrity checks.
"""
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Master verification secret. Can be overridden via RUBROL_LICENSE_SECRET.
_DEFAULT_VERIFY_SECRET = "rubrol_lic_sec_99482f0c774b6a01d3a5e8c1b4e2d3f7_master_cert"

@dataclass
class LicenseInfo:
    is_valid: bool
    tier: str  # "developer" | "pro_sidecar" | "eu_enterprise"
    customer_email: str
    github_username: Optional[str]
    features: List[str]
    issued_at: Optional[datetime]
    expires_at: Optional[datetime]
    days_remaining: int
    error: Optional[str] = None

    @property
    def is_commercial(self) -> bool:
        return self.is_valid and self.tier in ("pro_sidecar", "eu_enterprise")

    @property
    def has_eu_compliance(self) -> bool:
        return self.is_valid and self.tier == "eu_enterprise"


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data_str: str) -> bytes:
    padding = 4 - (len(data_str) % 4)
    if padding < 4:
        data_str += "=" * padding
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def generate_license_key(
    customer_email: str,
    github_username: str,
    tier: str = "pro_sidecar",
    valid_days: int = 365,
    custom_secret: Optional[str] = None,
) -> str:
    """
    Generate a cryptographically signed 1-year offline license key.
    Format: RBL-LIC-<b64_payload>.<b64_signature>
    """
    secret = (custom_secret or os.environ.get("RUBROL_LICENSE_SECRET") or _DEFAULT_VERIFY_SECRET).encode("utf-8")
    now_ts = int(time.time())
    exp_ts = now_ts + (valid_days * 86400)

    if tier == "eu_enterprise":
        features = [
            "unlimited_sidecar",
            "commercial_license",
            "pdfa_3b_iso19005_3",
            "facturx_zugferd_2_2",
            "en16931_schematron",
            "din5008_german",
            "chorus_pro_french",
            "priority_support",
        ]
    elif tier == "pro_sidecar":
        features = [
            "unlimited_sidecar",
            "commercial_license",
            "b2b_saas_templates",
            "standard_pdfa_2b",
            "vault_access",
        ]
    else:
        tier = "developer"
        features = ["local_cli", "watermarked_eval", "community_templates"]

    payload_dict = {
        "iss": "Rubrol Licensing Authority",
        "sub": customer_email.strip().lower(),
        "gh": github_username.strip().lstrip("@"),
        "tier": tier,
        "iat": now_ts,
        "exp": exp_ts,
        "feat": features,
    }

    payload_bytes = json.dumps(payload_dict, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = _b64_encode(payload_bytes)

    # Compute HMAC-SHA256 signature
    sig = hmac.new(secret, payload_bytes, hashlib.sha256).digest()
    sig_b64 = _b64_encode(sig)

    return f"RBL-LIC-{payload_b64}.{sig_b64}"


def verify_license_key(license_key_str: Optional[str] = None, custom_secret: Optional[str] = None) -> LicenseInfo:
    """
    Verify a signed Rubrol offline license key.
    If license_key_str is None, checks the RUBROL_LICENSE_KEY environment variable.
    """
    key = license_key_str or os.environ.get("RUBROL_LICENSE_KEY", "").strip()

    if not key:
        return LicenseInfo(
            is_valid=False,
            tier="developer",
            customer_email="",
            github_username=None,
            features=["local_cli", "watermarked_eval"],
            issued_at=None,
            expires_at=None,
            days_remaining=0,
            error="No license key provided (Running Developer Evaluation Build).",
        )

    if not key.startswith("RBL-LIC-"):
        return LicenseInfo(
            is_valid=False,
            tier="developer",
            customer_email="",
            github_username=None,
            features=[],
            issued_at=None,
            expires_at=None,
            days_remaining=0,
            error="Invalid license prefix. Expected 'RBL-LIC-...'",
        )

    raw_token = key[len("RBL-LIC-"):]
    if "." not in raw_token:
        return LicenseInfo(
            is_valid=False,
            tier="developer",
            customer_email="",
            github_username=None,
            features=[],
            issued_at=None,
            expires_at=None,
            days_remaining=0,
            error="Malformed license token structure.",
        )

    payload_b64, sig_b64 = raw_token.split(".", 1)

    try:
        payload_bytes = _b64_decode(payload_b64)
        sig_bytes = _b64_decode(sig_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        return LicenseInfo(
            is_valid=False,
            tier="developer",
            customer_email="",
            github_username=None,
            features=[],
            issued_at=None,
            expires_at=None,
            days_remaining=0,
            error=f"Failed to decode license payload: {e}",
        )

    secret = (custom_secret or os.environ.get("RUBROL_LICENSE_SECRET") or _DEFAULT_VERIFY_SECRET).encode("utf-8")
    expected_sig = hmac.new(secret, payload_bytes, hashlib.sha256).digest()

    if not hmac.compare_digest(sig_bytes, expected_sig):
        return LicenseInfo(
            is_valid=False,
            tier="developer",
            customer_email="",
            github_username=None,
            features=[],
            issued_at=None,
            expires_at=None,
            days_remaining=0,
            error="Cryptographic signature mismatch. License has been tampered with.",
        )

    now_ts = int(time.time())
    exp_ts = payload.get("exp", 0)
    iat_ts = payload.get("iat", 0)

    if now_ts > exp_ts:
        exp_date = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        return LicenseInfo(
            is_valid=False,
            tier=payload.get("tier", "developer"),
            customer_email=payload.get("sub", ""),
            github_username=payload.get("gh"),
            features=payload.get("feat", []),
            issued_at=datetime.fromtimestamp(iat_ts, tz=timezone.utc),
            expires_at=exp_date,
            days_remaining=0,
            error=f"License expired on {exp_date.strftime('%Y-%m-%d')}.",
        )

    days_remaining = max(0, int((exp_ts - now_ts) / 86400))
    tier = payload.get("tier", "pro_sidecar")

    return LicenseInfo(
        is_valid=True,
        tier=tier,
        customer_email=payload.get("sub", ""),
        github_username=payload.get("gh"),
        features=payload.get("feat", []),
        issued_at=datetime.fromtimestamp(iat_ts, tz=timezone.utc),
        expires_at=datetime.fromtimestamp(exp_ts, tz=timezone.utc),
        days_remaining=days_remaining,
        error=None,
    )


if __name__ == "__main__":
    if "--generate" in sys.argv:
        email = "enterprise@customer.de"
        github = "techlead"
        tier = "eu_enterprise"

        for i, arg in enumerate(sys.argv):
            if arg == "--email" and i + 1 < len(sys.argv):
                email = sys.argv[i + 1]
            elif arg == "--github" and i + 1 < len(sys.argv):
                github = sys.argv[i + 1]
            elif arg == "--tier" and i + 1 < len(sys.argv):
                tier = sys.argv[i + 1]

        key = generate_license_key(customer_email=email, github_username=github, tier=tier)
        print("Generated Rubrol License Key:")
        print(key)
        print("\nVerification Test:")
        info = verify_license_key(key)
        print(f"Valid: {info.is_valid} | Tier: {info.tier} | Days Remaining: {info.days_remaining}")
        print(f"Features: {', '.join(info.features)}")
    else:
        info = verify_license_key()
        print("Current Rubrol License Status:")
        print(f"Status: {'LICENSED (' + info.tier.upper() + ')' if info.is_valid else 'DEVELOPER EVALUATION'}")
        if info.error:
            print(f"Note: {info.error}")
        if info.is_valid:
            print(f"Customer: {info.customer_email} (@{info.github_username})")
            print(f"Expires: {info.expires_at.strftime('%Y-%m-%d')} ({info.days_remaining} days remaining)")
            print(f"Features: {', '.join(info.features)}")
