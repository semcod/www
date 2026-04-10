"""User and subscription database operations."""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional
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
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn


def convert_query(query: str) -> str:
    """Convert query placeholders based on DB_TYPE.
    PostgreSQL uses %s, SQLite uses ?.
    """
    if not USE_POSTGRES:
        return query.replace("%s", "?")
    return query


def execute_query(cursor, query: str, params: tuple = ()):
    """Execute query with automatic placeholder conversion."""
    query = convert_query(query)
    return cursor.execute(query, params)


def upsert_user(github_id: int, login: str, name: str, avatar_url: str, github_token: str) -> Dict:
    """Create or update a user. Returns the user dict."""
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()
    execute_query(cursor, "SELECT id FROM users WHERE github_id = %s", (github_id,))
    row = cursor.fetchone()

    if row:
        execute_query(cursor, """
            UPDATE users SET login=%s, name=%s, avatar_url=%s, github_token=%s, updated_at=%s
            WHERE github_id=%s
        """, (login, name, avatar_url, github_token, now, github_id))
        user_id = row["id"]
    else:
        execute_query(cursor, """
            INSERT INTO users (github_id, login, name, avatar_url, github_token)
            VALUES (%s, %s, %s, %s, %s)
        """, (github_id, login, name, avatar_url, github_token))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return {"id": user_id, "github_id": github_id, "login": login, "name": name, "avatar_url": avatar_url}


def get_user_by_github_id(github_id: int) -> Optional[Dict]:
    """Get user by GitHub ID."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT * FROM users WHERE github_id = %s", (github_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by internal ID."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_subscription(user_id: int) -> Optional[Dict]:
    """Get active subscription for a user. Returns None if not found (treat as free)."""
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, 
        "SELECT * FROM subscriptions WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_subscription(user_id: int, plan: str, stripe_customer_id: str = "",
                         stripe_subscription_id: str = "", status: str = "active") -> Dict:
    """Create or update subscription for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    execute_query(cursor, "SELECT id FROM subscriptions WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    if row:
        execute_query(cursor, """
            UPDATE subscriptions
            SET plan=%s, stripe_customer_id=%s, stripe_subscription_id=%s, status=%s, updated_at=%s
            WHERE user_id=%s
        """, (plan, stripe_customer_id, stripe_subscription_id, status, now, user_id))
    else:
        execute_query(cursor, """
            INSERT INTO subscriptions (user_id, plan, stripe_customer_id, stripe_subscription_id, status, week_reset_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, plan, stripe_customer_id, stripe_subscription_id, status, now))

    conn.commit()
    conn.close()
    return get_subscription(user_id)


def increment_scan_count(user_id: int) -> int:
    """Increment scans_this_week counter. Resets if a new week has started. Returns new count."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    execute_query(cursor, "SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    if not row:
        execute_query(cursor, """
            INSERT INTO subscriptions (user_id, plan, scans_this_week, week_reset_at)
            VALUES (%s, 'free', 1, %s)
        """, (user_id, now_iso))
        conn.commit()
        conn.close()
        return 1

    week_reset_at = row["week_reset_at"]
    scans = row["scans_this_week"]

    if week_reset_at:
        try:
            reset_dt = datetime.fromisoformat(week_reset_at.replace("Z", "+00:00"))
            if (now - reset_dt).days >= 7:
                scans = 0
                week_reset_at = now_iso
        except ValueError:
            week_reset_at = now_iso
            scans = 0
    else:
        week_reset_at = now_iso

    new_count = scans + 1
    execute_query(cursor, """
        UPDATE subscriptions SET scans_this_week=%s, week_reset_at=%s, updated_at=%s
        WHERE user_id=%s
    """, (new_count, week_reset_at, now_iso, user_id))
    conn.commit()
    conn.close()
    return new_count
