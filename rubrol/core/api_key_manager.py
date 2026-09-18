# -*- coding: utf-8 -*-
"""
Rubrol API Key & Quota Manager
Ultra-fast, zero-dependency SQLite-backed credential and rate limiting engine.
Supports instant free trial keys (no credit card required) and paid tier subscriptions.
"""
import os
import sqlite3
import secrets
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "auth.sqlite3"

# Default tier quotas
TIER_QUOTAS = {
    "trial": 30,          # 30 free renders, no card required
    "starter": 2500,      # $29/mo - 2,500 docs/mo
    "pro": 15000,         # $79/mo - 15,000 docs/mo + Factur-X / PDF/A-3
    "scale": 75000,       # $249/mo - 75,000 docs/mo
    "unlimited": 999999999
}

class APIKeyManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT UNIQUE NOT NULL,
                    email TEXT,
                    tier TEXT NOT NULL DEFAULT 'trial',
                    quota_limit INTEGER NOT NULL DEFAULT 30,
                    quota_used INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    created_at REAL NOT NULL,
                    last_used_at REAL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_key ON api_keys(api_key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_email ON api_keys(email);")
            conn.commit()

    def create_trial_key(self, email: str = "") -> Dict[str, Any]:
        """
        Generate an instant free trial API key with 30 free requests.
        No credit card required.
        """
        token = secrets.token_hex(16)
        api_key = f"rbl_trial_{token}"
        quota = TIER_QUOTAS["trial"]
        now = time.time()
        clean_email = email.strip().lower() if email else f"trial_{token[:8]}@anonymous.rubrol.com"

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO api_keys (api_key, email, tier, quota_limit, quota_used, is_active, created_at)
                VALUES (?, ?, 'trial', ?, 0, 1, ?)
            """, (api_key, clean_email, quota, now))
            conn.commit()

        return {
            "api_key": api_key,
            "email": clean_email,
            "tier": "trial",
            "quota_limit": quota,
            "quota_used": 0,
            "quota_remaining": quota,
            "created_at": now
        }

    def provision_paid_key(
        self,
        email: str,
        tier: str = "starter",
        stripe_customer_id: str = "",
        stripe_subscription_id: str = ""
    ) -> Dict[str, Any]:
        """
        Provision or upgrade an API key for a paying customer.
        """
        tier = tier.lower()
        quota = TIER_QUOTAS.get(tier, TIER_QUOTAS["starter"])
        token = secrets.token_hex(20)
        api_key = f"rbl_live_{token}"
        now = time.time()
        clean_email = email.strip().lower()

        with self._get_conn() as conn:
            # Check if customer already has a key to update or create a new one
            existing = conn.execute("SELECT * FROM api_keys WHERE email = ? AND is_active = 1", (clean_email,)).fetchone()
            if existing:
                conn.execute("""
                    UPDATE api_keys
                    SET tier = ?, quota_limit = ?, stripe_customer_id = ?, stripe_subscription_id = ?
                    WHERE id = ?
                """, (tier, quota, stripe_customer_id, stripe_subscription_id, existing["id"]))
                conn.commit()
                return self.get_key_info(existing["api_key"]) # type: ignore
            else:
                conn.execute("""
                    INSERT INTO api_keys (api_key, email, tier, quota_limit, quota_used, is_active, stripe_customer_id, stripe_subscription_id, created_at)
                    VALUES (?, ?, ?, ?, 0, 1, ?, ?, ?)
                """, (api_key, clean_email, tier, quota, stripe_customer_id, stripe_subscription_id, now))
                conn.commit()

        return {
            "api_key": api_key,
            "email": clean_email,
            "tier": tier,
            "quota_limit": quota,
            "quota_used": 0,
            "quota_remaining": quota,
            "created_at": now
        }

    def validate_and_consume(self, api_key: str, cost: int = 1) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Atomically validate API key and consume quota.
        Returns: (success: bool, info: Optional[Dict], error_code: Optional[str])
        Error codes:
          - 'missing_key'
          - 'invalid_key'
          - 'key_inactive'
          - 'quota_exceeded'
        """
        if not api_key:
            return False, None, "missing_key"

        clean_key = api_key.strip()
        if clean_key.lower().startswith("bearer "):
            clean_key = clean_key[7:].strip()

        now = time.time()
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM api_keys WHERE api_key = ?", (clean_key,)).fetchone()
            if not row:
                return False, None, "invalid_key"

            if not row["is_active"]:
                return False, None, "key_inactive"

            limit = row["quota_limit"]
            used = row["quota_used"]
            remaining = limit - used

            if remaining < cost:
                info = {
                    "api_key": clean_key,
                    "tier": row["tier"],
                    "quota_limit": limit,
                    "quota_used": used,
                    "quota_remaining": 0
                }
                return False, info, "quota_exceeded"

            # Atomically increment used quota
            conn.execute("""
                UPDATE api_keys
                SET quota_used = quota_used + ?, last_used_at = ?
                WHERE id = ?
            """, (cost, now, row["id"]))
            conn.commit()

            new_used = used + cost
            info = {
                "api_key": clean_key,
                "tier": row["tier"],
                "quota_limit": limit,
                "quota_used": new_used,
                "quota_remaining": max(0, limit - new_used),
                "email": row["email"]
            }
            return True, info, None

    def get_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get status and remaining quota for an API key."""
        clean_key = api_key.strip()
        if clean_key.lower().startswith("bearer "):
            clean_key = clean_key[7:].strip()

        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM api_keys WHERE api_key = ?", (clean_key,)).fetchone()
            if not row:
                return None

            limit = row["quota_limit"]
            used = row["quota_used"]
            return {
                "api_key": clean_key,
                "email": row["email"],
                "tier": row["tier"],
                "quota_limit": limit,
                "quota_used": used,
                "quota_remaining": max(0, limit - used),
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"],
                "last_used_at": row["last_used_at"]
            }

# Global singleton instance
key_manager = APIKeyManager()
