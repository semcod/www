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

"""Installation database operations."""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from config import DB_PATH


def create_installation(tenant_id: int, repository_id: int, apps: List[str],
                        webhook_id: str = "", webhook_secret: str = "") -> Dict:
    """Create app installation for a repository."""
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO installations (
            tenant_id, repository_id, apps, webhook_id, webhook_secret,
            installed_at, updated_at, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
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
        SELECT * FROM installations WHERE tenant_id = %s AND repository_id = %s
    """, (tenant_id, repository_id))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else {}


def get_installation(tenant_id: int, repository_id: int) -> Optional[Dict]:
    """Get installation by tenant and repository."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = %s AND i.repository_id = %s
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, r.full_name as repo_full_name, r.provider as repo_provider
        FROM installations i
        JOIN repositories r ON i.repository_id = r.id
        WHERE i.tenant_id = %s
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE installations SET status='inactive', updated_at=%s
        WHERE tenant_id = %s AND repository_id = %s
    """, (datetime.now(timezone.utc).isoformat(), tenant_id, repository_id))

    conn.commit()
    conn.close()
    return True


def update_installation_scan(tenant_id: int, repository_id: int, score: int):
    """Update last scan info for installation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE installations SET last_scan_at=%s, last_scan_score=%s, updated_at=%s
        WHERE tenant_id = %s AND repository_id = %s
    """, (datetime.now(timezone.utc).isoformat(), score, datetime.now(timezone.utc).isoformat(),
          tenant_id, repository_id))

    conn.commit()
    conn.close()
