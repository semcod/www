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

"""Repository database operations."""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional
from config import DB_PATH


def get_or_create_repository(tenant_id: int, provider: str, repo_provider_id: str,
                             name: str, full_name: str, description: str = "",
                             private: bool = False, default_branch: str = "main",
                             web_url: str = "", clone_url: str = "") -> Dict:
    """Get existing repository or create new one for tenant."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    # Try to get existing
    cursor.execute(f"""
        SELECT * FROM repositories
        WHERE tenant_id = {placeholder} AND provider = {placeholder} AND full_name = {placeholder}
    """, (tenant_id, provider, full_name))
    row = cursor.fetchone()

    if row:
        conn.close()
        row_dict = row if isinstance(row, dict) else dict(row)
        return {**row_dict, "is_new": False}

    # Create new
    now = datetime.now(timezone.utc).isoformat()
    placeholders = ", ".join([placeholder] * 12)
    cursor.execute(f"""
        INSERT INTO repositories (
            tenant_id, provider, repo_provider_id, name, full_name,
            description, private, default_branch, web_url, clone_url, created_at, updated_at
        ) VALUES ({placeholders})
    """, (tenant_id, provider, repo_provider_id, name, full_name,
          description, 1 if private else 0, default_branch, web_url, clone_url, now, now))

    repo_id = cursor.lastrowid
    conn.commit()

    cursor.execute(f"SELECT * FROM repositories WHERE id = {placeholder}", (repo_id,))
    row = cursor.fetchone()
    conn.close()

    row_dict = row if isinstance(row, dict) else dict(row)
    return {**row_dict, "is_new": True}


def get_tenant_repositories(tenant_id: int) -> List[Dict]:
    """Get all repositories for a tenant."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        SELECT * FROM repositories WHERE tenant_id = {placeholder} ORDER BY updated_at DESC
    """, (tenant_id,))

    rows = cursor.fetchall()
    conn.close()

    return [row if isinstance(row, dict) else dict(row) for row in rows]


def get_repository_by_full_name(tenant_id: int, provider: str, full_name: str) -> Optional[Dict]:
    """Get repository by tenant + provider + full_name."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        SELECT * FROM repositories
        WHERE tenant_id = {placeholder} AND provider = {placeholder} AND full_name = {placeholder}
    """, (tenant_id, provider, full_name))

    row = cursor.fetchone()
    conn.close()
    return row if row else None
