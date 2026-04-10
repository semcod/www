"""SQLite database for scan history persistence."""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional


DB_PATH = Path("scans.db")


def init_db():
    """Initialize the database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            health_score INTEGER,
            grade TEXT,
            stats TEXT,
            completed TEXT,
            sandbox INTEGER DEFAULT 0,
            badge_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_id INTEGER UNIQUE NOT NULL,
            login TEXT NOT NULL,
            name TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            github_token TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_scan(scan_data: Dict) -> int:
    """Save a scan to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO scans (repo, health_score, grade, stats, completed, sandbox, badge_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_data["repo"],
        scan_data["health_score"],
        scan_data["grade"],
        json.dumps(scan_data["stats"]),
        scan_data["completed"],
        1 if scan_data.get("sandbox") else 0,
        scan_data.get("badge_url", ""),
    ))
    
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return scan_id


def get_recent_scans(limit: int = 100) -> List[Dict]:
    """Get recent scans from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT repo, health_score, grade, stats, completed, sandbox, badge_url
        FROM scans
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    scans = []
    for row in rows:
        scans.append({
            "repo": row["repo"],
            "health_score": row["health_score"],
            "grade": row["grade"],
            "stats": json.loads(row["stats"]),
            "completed": row["completed"],
            "sandbox": bool(row["sandbox"]),
            "badge_url": row["badge_url"],
        })
    
    return scans


def get_total_scan_count() -> int:
    """Get total number of scans in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scans")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


def upsert_user(github_id: int, login: str, name: str, avatar_url: str, github_token: str) -> Dict:
    """Create or update a user. Returns the user dict."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("SELECT id FROM users WHERE github_id = ?", (github_id,))
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE users SET login=?, name=?, avatar_url=?, github_token=?, updated_at=?
            WHERE github_id=?
        """, (login, name, avatar_url, github_token, now, github_id))
        user_id = row["id"]
    else:
        cursor.execute("""
            INSERT INTO users (github_id, login, name, avatar_url, github_token)
            VALUES (?, ?, ?, ?, ?)
        """, (github_id, login, name, avatar_url, github_token))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return {"id": user_id, "github_id": github_id, "login": login, "name": name, "avatar_url": avatar_url}


def get_user_by_github_id(github_id: int) -> Optional[Dict]:
    """Get user by GitHub ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE github_id = ?", (github_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by internal ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


# Initialize database on import
init_db()
