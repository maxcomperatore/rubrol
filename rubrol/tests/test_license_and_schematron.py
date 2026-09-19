# -*- coding: utf-8 -*-
"""
Tests for Rubrol Cryptographic Offline Licensing and Schematron Business Rules Validator.
"""
import pytest
from rubrol.core.license import generate_license_key, verify_license_key
from rubrol.facturx.schematron_validator import schematron_validator
from rubrol.facturx.generator import generate_facturx_xml

def test_offline_license_generation_and_verification():
    email = "cto@valitool.de"
    github = "sgraefe"
    tier = "eu_enterprise"

    key = generate_license_key(customer_email=email, github_username=github, tier=tier, valid_days=365)
    assert key.startswith("RBL-LIC-")
    assert "." in key

    info = verify_license_key(key)
    assert info.is_valid is True
    assert info.tier == "eu_enterprise"
    assert info.customer_email == email
    assert info.github_username == github
    assert info.days_remaining in (364, 365)
    assert info.is_commercial is True
    assert info.has_eu_compliance is True
    assert "din5008_german" in info.features
    assert "en16931_schematron" in info.features

def test_offline_license_tampering_detection():
    key = generate_license_key(customer_email="user@domain.com", github_username="user", tier="pro_sidecar")
    # Tamper with the token
    tampered_key = key[:-4] + "XXXX"
    info = verify_license_key(tampered_key)
    assert info.is_valid is False
    assert "Cryptographic signature mismatch" in info.error

def test_developer_evaluation_default():
    info = verify_license_key("")
    assert info.is_valid is False
    assert info.tier == "developer"
    assert info.is_commercial is False

def test_schematron_valid_xml():
    test_data = {
        "invoice_number": "RE-2026-TEST",
        "issued_date": "2026-09-19",
        "currency": "EUR",
        "vendor": {"name": "Rubrol Systems GmbH", "country": "DE", "vat_id": "DE345678901"},
        "customer": {"name": "Customer AG", "country": "DE", "vat_id": "DE987654321"},
        "line_items": [{"name": "Software License", "qty": 1, "unit_price": 1800.00, "tax_rate": 0.19}],
    }
    xml_str = generate_facturx_xml(test_data, profile="EN16931")
    valid, errors = schematron_validator.validate_xml_string(xml_str, profile="EN16931")
    assert valid is True
    assert len(errors) == 0

def test_schematron_catches_invalid_syntax():
    valid, errors = schematron_validator.validate_xml_string("<not-even-closed>")
    assert valid is False
    assert len(errors) > 0
    assert errors[0].rule_id == "XML-SYNTAX"

def test_stripe_subscription_cancellation_webhook(monkeypatch):
    from rubrol.webhooks.stripe_fulfillment import process_stripe_event
    from rubrol.core.api_key_manager import key_manager

    # Mock token and HTTP deletion
    monkeypatch.setattr("rubrol.webhooks.stripe_fulfillment.get_github_token", lambda: "fake_token")
    monkeypatch.setattr("rubrol.webhooks.stripe_fulfillment.remove_github_user_from_repo", lambda user, repo: {"success": True, "username": user, "repository": repo})

    # Test cancellation event
    event = {
        "id": "evt_test_cancel_123",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_test_annual_999",
                "customer": "cus_test_123",
                "metadata": {
                    "github_username": "canceluser"
                }
            }
        }
    }
    result = process_stripe_event(event)
    assert result["handled"] is True
    assert result["subscription_id"] == "sub_test_annual_999"
    assert result["github_username"] == "canceluser"
    assert len(result["revocations"]) == 2

def test_stripe_subscription_renewal_webhook():
    from rubrol.webhooks.stripe_fulfillment import process_stripe_event
    from rubrol.core.license import verify_license_key

    event = {
        "id": "evt_test_renewal_123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "billing_reason": "subscription_cycle",
                "customer_email": "renewed@client.de",
                "amount_paid": 480000,
                "lines": {
                    "data": [
                        {
                            "metadata": {
                                "tier": "eu_enterprise",
                                "github_username": "renewedclient"
                            }
                        }
                    ]
                }
            }
        }
    }
    result = process_stripe_event(event)
    assert result["handled"] is True
    assert result["tier"] == "eu_enterprise"
    assert result["customer_email"] == "renewed@client.de"
    assert "license_key" in result
    info = verify_license_key(result["license_key"])
    assert info.is_valid is True
    assert info.tier == "eu_enterprise"
    assert info.days_remaining in (364, 365)

