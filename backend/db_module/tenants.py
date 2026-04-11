"""Tenant database operations."""

import sqlite3
from datetime import datetime, timezone
from config import DB_PATH
from .db_connection import get_connection, USE_POSTGRES
from typing import Dict, Optional


def get_or_create_tenant(provider: str, provider_user_id: str, login: str,
                          name: str = "", email: str = "", avatar_url: str = "") -> Dict:
    """Get existing tenant or create new one."""
    conn = get_connection()
    cursor = conn.cursor()

    # Use appropriate placeholder based on database type
    placeholder = "%s" if USE_POSTGRES else "?"

    # Try to get existing
    cursor.execute(f"""
        SELECT * FROM tenants WHERE provider = {placeholder} AND provider_user_id = {placeholder}
    """, (provider, provider_user_id))
    row = cursor.fetchone()

    if row:
        conn.close()
        # row is already a dict when using RealDictCursor, otherwise convert to dict
        row_dict = row if isinstance(row, dict) else dict(row)
        return {**row_dict, "is_new": False}

    # Create new tenant
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(f"""
        INSERT INTO tenants (provider, provider_user_id, login, name, email, avatar_url, created_at, updated_at)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """, (provider, provider_user_id, login, name, email, avatar_url, now, now))

    tenant_id = cursor.lastrowid
    conn.commit()

    cursor.execute(f"SELECT * FROM tenants WHERE id = {placeholder}", (tenant_id,))
    row = cursor.fetchone()
    conn.close()

    row_dict = row if isinstance(row, dict) else dict(row)
    return {**row_dict, "is_new": True}


def get_tenant_by_id(tenant_id: int) -> Optional[Dict]:
    """Get tenant by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(f"SELECT * FROM tenants WHERE id = {placeholder}", (tenant_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None


def update_tenant_plan(tenant_id: int, plan: str,
                       billing_customer_id: str = "",
                       billing_subscription_id: str = "") -> Optional[Dict]:
    """Update tenant's billing plan."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute(f"""
        UPDATE tenants SET plan={placeholder}, billing_customer_id={placeholder}, billing_subscription_id={placeholder}, updated_at={placeholder}
        WHERE id={placeholder}
    """, (plan, billing_customer_id, billing_subscription_id, now, tenant_id))

    conn.commit()
    conn.close()
    return get_tenant_by_id(tenant_id)
