from config import DB_PATH, DB_TYPE, DATABASE_URL

# Try to use psycopg2 for PostgreSQL if available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = (DB_TYPE == "postgresql")
except ImportError:
    USE_POSTGRES = False


def get_connection():
    """Get database connection based on DB_TYPE."""
    if USE_POSTGRES and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable dict-like access for SQLite
        return conn

"""Tenant database operations."""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional
from config import DB_PATH


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
