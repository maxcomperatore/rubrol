# -*- coding: utf-8 -*-
"""
Rubrol Stripe Product & Checkout Link Generator.
Provisions the 2 Annual Commercial Products in Stripe (Sidekiq Model):
1. Rubrol Pro ($1,800 / year)
2. Rubrol Enterprise ($4,800 / year)
Configures custom_fields to require the buyer's GitHub username at checkout.
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("rubrol.stripe.setup")

def create_checkout_session(
    tier: str = "pro",
    success_url: str = "https://rubrol.com/?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: str = "https://rubrol.com/#pricing",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session with the required GitHub username custom field.
    """
    import stripe
    stripe.api_key = api_key or os.environ.get("STRIPE_SECRET_KEY")

    if not stripe.api_key:
        return {
            "error": "STRIPE_SECRET_KEY environment variable not set.",
            "instructions": "Set STRIPE_SECRET_KEY=sk_test_... or sk_live_... to create live Stripe Checkout sessions."
        }

    if tier.lower() in ("enterprise", "rubrol_enterprise", "compliance"):
        name = "Rubrol Enterprise (Annual License)"
        description = (
            "Complete enterprise e-invoicing suite. Everything in Pro plus certified ISO 19005-3 PDF/A-3b & "
            "Factur-X / ZUGFeRD 2.2 Schematron semantic validator, German DIN 5008 & French Chorus Pro XML/PDF, "
            "dual vault access (rubrol-enterprise-vault), guaranteed compliance updates for 2025-2028 EU mandates, "
            "air-gapped license key, and direct priority engineering support."
        )
        amount = 480000  # $4,800.00 USD in cents
        metadata = {"tier": "enterprise", "plan": "rubrol_enterprise"}
    else:
        name = "Rubrol Pro (Annual Commercial License)"
        description = (
            "Commercial open-core license for scaling engineering teams. Unlimited local Docker containers, "
            "replaces LGPLv3 with full commercial production rights, zero Chrome memory leaks (<6ms renders), "
            "pre-built B2B SaaS invoice & receipt templates, dynamic Swiss QR / barcodes, private GitHub vault "
            "(rubrol-pro-vault) access, and a signed 1-year offline cryptographic license key."
        )
        amount = 180000  # $1,800.00 USD in cents
        metadata = {"tier": "pro", "plan": "rubrol_pro"}

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": name,
                        "description": description,
                    },
                    "unit_amount": amount,
                    "recurring": {"interval": "year"},
                },
                "quantity": 1,
            }],
            mode="subscription",
            metadata=metadata,
            custom_fields=[{
                "key": "github_username",
                "label": {"type": "custom", "custom": "GitHub Username (for Vault Access)"},
                "type": "text",
                "optional": False,
            }],
            allow_promotion_codes=True,
            billing_address_collection="required",
            tax_id_collection={"enabled": True},
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "tier": metadata["tier"],
            "plan_name": name,
            "amount_usd": amount / 100,
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tier_arg = "enterprise" if ("--enterprise" in sys.argv or "-e" in sys.argv) else "pro"
    print(f"Generating Stripe Checkout Session for: {tier_arg.upper()}...")
    res = create_checkout_session(tier=tier_arg)
    print(json.dumps(res, indent=2))
