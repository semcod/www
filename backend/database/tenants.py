"""Tenant database operations."""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional
from config import DB_PATH


def get_or_create_tenant(provider: str, provider_user_id: str, login: str,
                          name: str = "", email: str = "", avatar_url: str = "") -> Dict:
    """Get existing tenant or create new one."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Try to get existing
    cursor.execute("""
        SELECT * FROM tenants WHERE provider = ? AND provider_user_id = ?
    """, (provider, provider_user_id))
    row = cursor.fetchone()

    if row:
        conn.close()
        return {**dict(row), "is_new": False}

    # Create new tenant
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO tenants (provider, provider_user_id, login, name, email, avatar_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (provider, provider_user_id, login, name, email, avatar_url, now, now))

    tenant_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    row = cursor.fetchone()
    conn.close()

    return {**dict(row), "is_new": True}


def get_tenant_by_id(tenant_id: int) -> Optional[Dict]:
    """Get tenant by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_tenant_plan(tenant_id: int, plan: str,
                       billing_customer_id: str = "",
                       billing_subscription_id: str = "") -> Optional[Dict]:
    """Update tenant's billing plan."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE tenants SET plan=?, billing_customer_id=?, billing_subscription_id=?, updated_at=?
        WHERE id=?
    """, (plan, billing_customer_id, billing_subscription_id, now, tenant_id))

    conn.commit()
    conn.close()
    return get_tenant_by_id(tenant_id)
