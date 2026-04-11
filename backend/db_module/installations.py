"""Installation database operations."""

import sqlite3
import json
from config import DB_PATH
from .db_connection import get_connection, USE_POSTGRES
from datetime import datetime, timezone
from typing import Dict, List, Optional


def create_installation(tenant_id: int, repository_id: int, apps: List[str],
                        webhook_id: str = "", webhook_secret: str = "") -> Dict:
    """Create app installation for a repository."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    now = datetime.now(timezone.utc).isoformat()

    if USE_POSTGRES:
        placeholders = ", ".join([placeholder] * 7)
        cursor.execute(f"""
            INSERT INTO installations (
                tenant_id, repository_id, apps, webhook_id, webhook_secret,
                installed_at, updated_at, status
            ) VALUES ({placeholders}, 'active')
            ON CONFLICT(tenant_id, repository_id) DO UPDATE SET
                apps=excluded.apps,
                webhook_id=excluded.webhook_id,
                webhook_secret=excluded.webhook_secret,
                updated_at=excluded.updated_at,
                status='active'
        """, (tenant_id, repository_id, json.dumps(apps), webhook_id, webhook_secret, now, now))
    else:
        # SQLite: use INSERT OR REPLACE
        placeholders = ", ".join([placeholder] * 8)
        cursor.execute(f"""
            INSERT OR REPLACE INTO installations (
                tenant_id, repository_id, apps, webhook_id, webhook_secret,
                installed_at, updated_at, status
            ) VALUES ({placeholders})
        """, (tenant_id, repository_id, json.dumps(apps), webhook_id, webhook_secret, now, now, 'active'))

    conn.commit()

    # Get the installation
    cursor.execute(f"""
        SELECT * FROM installations WHERE tenant_id = {placeholder} AND repository_id = {placeholder}
    """, (tenant_id, repository_id))
    row = cursor.fetchone()
    conn.close()

    return row if row else {}


def get_installation(tenant_id: int, repository_id: int) -> Optional[Dict]:
    """Get installation by tenant and repository."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = {placeholder} AND i.repository_id = {placeholder}
    """, (tenant_id, repository_id))

    row = cursor.fetchone()
    conn.close()

    if row:
        result = row if isinstance(row, dict) else dict(row)
        result["apps"] = json.loads(result.get("apps", "[]"))
        return result
    return None


def get_tenant_installations(tenant_id: int) -> List[Dict]:
    """Get all installations for a tenant."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = {placeholder}
    """, (tenant_id,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        result = row if isinstance(row, dict) else dict(row)
        result["apps"] = json.loads(result.get("apps", "[]"))
        results.append(result)
    return results


def delete_installation(tenant_id: int, repository_id: int) -> bool:
    """Delete installation (soft delete - set inactive)."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        UPDATE installations SET status='inactive', updated_at={placeholder}
        WHERE tenant_id = {placeholder} AND repository_id = {placeholder}
    """, (datetime.now(timezone.utc).isoformat(), tenant_id, repository_id))

    conn.commit()
    conn.close()
    return True


def update_installation_scan(tenant_id: int, repository_id: int, score: int):
    """Update last scan info for installation."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if USE_POSTGRES else "?"

    cursor.execute(f"""
        UPDATE installations SET last_scan_at={placeholder}, last_scan_score={placeholder}, updated_at={placeholder}
        WHERE tenant_id = {placeholder} AND repository_id = {placeholder}
    """, (datetime.now(timezone.utc).isoformat(), score, datetime.now(timezone.utc).isoformat(),
          tenant_id, repository_id))

    conn.commit()
    conn.close()
