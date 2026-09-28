# -*- coding: utf-8 -*-
"""
Tests for APIKeyManager SQLite engine, atomic quota guards, and subscription provisioning.
"""
import pytest
from pathlib import Path
from rubrol.core.api_key_manager import APIKeyManager, TIER_QUOTAS

@pytest.fixture
def temp_manager(tmp_path):
    db_file = tmp_path / "test_auth.sqlite3"
    return APIKeyManager(db_path=db_file)

def test_create_trial_key(temp_manager):
    res = temp_manager.create_trial_key(email="trial@example.com")
    assert res["api_key"].startswith("rbl_trial_")
    assert res["email"] == "trial@example.com"
    assert res["tier"] == "trial"
    assert res["quota_limit"] == TIER_QUOTAS["trial"]
    assert res["quota_used"] == 0
    assert res["quota_remaining"] == TIER_QUOTAS["trial"]

def test_validate_and_consume_quota(temp_manager):
    key_info = temp_manager.create_trial_key()
    api_key = key_info["api_key"]

    # Consume 5 units
    success, info, err = temp_manager.validate_and_consume(api_key, cost=5)
    assert success is True
    assert err is None
    assert info["quota_used"] == 5
    assert info["quota_remaining"] == TIER_QUOTAS["trial"] - 5

    # Consume remaining units
    rem = info["quota_remaining"]
    success, info, err = temp_manager.validate_and_consume(api_key, cost=rem)
    assert success is True
    assert info["quota_remaining"] == 0

    # Next attempt must fail with quota_exceeded
    success, info, err = temp_manager.validate_and_consume(api_key, cost=1)
    assert success is False
    assert err == "quota_exceeded"
    assert info["quota_remaining"] == 0

def test_invalid_and_missing_keys(temp_manager):
    # Empty key
    success, info, err = temp_manager.validate_and_consume("")
    assert success is False
    assert err == "missing_key"

    # Non-existent key
    success, info, err = temp_manager.validate_and_consume("rbl_invalid_token_12345")
    assert success is False
    assert err == "invalid_key"

def test_provision_paid_key_and_upgrade(temp_manager):
    # Provision new paid key
    res = temp_manager.provision_paid_key(
        email="customer@acme.com",
        tier="pro",
        stripe_customer_id="cus_12345",
        stripe_subscription_id="sub_67890"
    )
    assert res["tier"] == "pro"
    assert res["quota_limit"] == TIER_QUOTAS["pro"]
    assert res["api_key"].startswith("rbl_live_")

    # Upgrade existing customer to scale tier
    upgraded = temp_manager.provision_paid_key(
        email="customer@acme.com",
        tier="scale"
    )
    assert upgraded["tier"] == "scale"
    assert upgraded["quota_limit"] == TIER_QUOTAS["scale"]
    assert upgraded["api_key"] == res["api_key"]

def test_bearer_prefix_parsing(temp_manager):
    key_info = temp_manager.create_trial_key()
    bearer_token = f"Bearer {key_info['api_key']}"
    success, info, err = temp_manager.validate_and_consume(bearer_token, cost=1)
    assert success is True
    assert info["quota_used"] == 1
