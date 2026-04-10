"""Event queue database operations."""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from config import DB_PATH


def queue_event(event_id: str, event_type: str, provider: str,
                repo_full_name: str, pr_id: Optional[int], payload: Dict) -> int:
    """Queue a new event for processing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (event_id, type, provider, repo_full_name, pr_id, payload, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (event_id, event_type, provider, repo_full_name, pr_id, json.dumps(payload)))

    event_db_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return event_db_id


def get_pending_events(limit: int = 100) -> List[Dict]:
    """Get pending events for processing."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events WHERE status = 'pending' ORDER BY created_at ASC LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        result = dict(row)
        result["payload"] = json.loads(result.get("payload", "{}"))
        results.append(result)
    return results


def update_event_status(event_id: int, status: str, error_message: str = ""):
    """Update event processing status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status == "completed":
        cursor.execute("""
            UPDATE events SET status=?, processed_at=?, error_message=''
            WHERE id=?
        """, (status, datetime.now(timezone.utc).isoformat(), event_id))
    elif status == "failed":
        cursor.execute("""
            UPDATE events SET status=?, error_message=?, retry_count=retry_count+1
            WHERE id=?
        """, (status, error_message, event_id))
    else:
        cursor.execute("""
            UPDATE events SET status=?, error_message='' WHERE id=?
        """, (status, event_id))

    conn.commit()
    conn.close()
