from config import DB_PATH, DB_TYPE, DATABASE_URL

# Try to use psycopg2 for PostgreSQL if available
try:
    import psycopg2
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

    # Try to get existing
    cursor.execute("""
        SELECT * FROM tenants WHERE provider = %s AND provider_user_id = %s
    """, (provider, provider_user_id))
    row = cursor.fetchone()

    if row:
        conn.close()
        return {**dict(row), "is_new": False}

    # Create new tenant
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO tenants (provider, provider_user_id, login, name, email, avatar_url, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (provider, provider_user_id, login, name, email, avatar_url, now, now))

    tenant_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM tenants WHERE id = %s", (tenant_id,))
    row = cursor.fetchone()
    conn.close()

    return {**dict(row), "is_new": True}


def get_tenant_by_id(tenant_id: int) -> Optional[Dict]:
    """Get tenant by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE id = %s", (tenant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_tenant_plan(tenant_id: int, plan: str,
                       billing_customer_id: str = "",
                       billing_subscription_id: str = "") -> Optional[Dict]:
    """Update tenant's billing plan."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE tenants SET plan=%s, billing_customer_id=%s, billing_subscription_id=%s, updated_at=%s
        WHERE id=%s
    """, (plan, billing_customer_id, billing_subscription_id, now, tenant_id))

    conn.commit()
    conn.close()
    return get_tenant_by_id(tenant_id)
