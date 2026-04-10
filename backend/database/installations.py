"""Installation database operations."""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from config import DB_PATH


def create_installation(tenant_id: int, repository_id: int, apps: List[str],
                        webhook_id: str = "", webhook_secret: str = "") -> Dict:
    """Create app installation for a repository."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO installations (
            tenant_id, repository_id, apps, webhook_id, webhook_secret,
            installed_at, updated_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        ON CONFLICT(tenant_id, repository_id) DO UPDATE SET
            apps=excluded.apps,
            webhook_id=excluded.webhook_id,
            webhook_secret=excluded.webhook_secret,
            updated_at=excluded.updated_at,
            status='active'
    """, (tenant_id, repository_id, json.dumps(apps), webhook_id, webhook_secret, now, now))

    conn.commit()

    # Get the installation
    cursor.execute("""
        SELECT * FROM installations WHERE tenant_id = ? AND repository_id = ?
    """, (tenant_id, repository_id))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else {}


def get_installation(tenant_id: int, repository_id: int) -> Optional[Dict]:
    """Get installation by tenant and repository."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = ? AND i.repository_id = ?
    """, (tenant_id, repository_id))

    row = cursor.fetchone()
    conn.close()

    if row:
        result = dict(row)
        result["apps"] = json.loads(result.get("apps", "[]"))
        return result
    return None


def get_tenant_installations(tenant_id: int) -> List[Dict]:
    """Get all installations for a tenant."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = ?
    """, (tenant_id,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        result = dict(row)
        result["apps"] = json.loads(result.get("apps", "[]"))
        results.append(result)
    return results


def delete_installation(tenant_id: int, repository_id: int) -> bool:
    """Delete installation (soft delete - set inactive)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE installations SET status='inactive', updated_at=?
        WHERE tenant_id = ? AND repository_id = ?
    """, (datetime.now(timezone.utc).isoformat(), tenant_id, repository_id))

    conn.commit()
    conn.close()
    return True


def update_installation_scan(tenant_id: int, repository_id: int, score: int):
    """Update last scan info for installation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE installations SET last_scan_at=?, last_scan_score=?, updated_at=?
        WHERE tenant_id = ? AND repository_id = ?
    """, (datetime.now(timezone.utc).isoformat(), score, datetime.now(timezone.utc).isoformat(),
          tenant_id, repository_id))

    conn.commit()
    conn.close()
