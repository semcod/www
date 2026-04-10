"""SQLite database for scan history persistence."""

import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional

from config import DB_PATH


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
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            stripe_customer_id TEXT DEFAULT '',
            stripe_subscription_id TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'active',
            scans_this_week INTEGER DEFAULT 0,
            week_reset_at TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def get_repo_scans(repo: str, limit: int = 100) -> List[Dict]:
    """Get scans for a specific repository ordered by date ascending."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT repo, health_score, grade, stats, completed, sandbox, badge_url
        FROM scans
        WHERE repo = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (repo, limit))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "repo": row["repo"],
            "health_score": row["health_score"],
            "grade": row["grade"],
            "stats": json.loads(row["stats"]),
            "completed": row["completed"],
            "sandbox": bool(row["sandbox"]),
            "badge_url": row["badge_url"],
        }
        for row in rows
    ]


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


def get_subscription(user_id: int) -> Optional[Dict]:
    """Get active subscription for a user. Returns None if not found (treat as free)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_subscription(user_id: int, plan: str, stripe_customer_id: str = "",
                         stripe_subscription_id: str = "", status: str = "active") -> Dict:
    """Create or update subscription for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("SELECT id FROM subscriptions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE subscriptions
            SET plan=?, stripe_customer_id=?, stripe_subscription_id=?, status=?, updated_at=?
            WHERE user_id=?
        """, (plan, stripe_customer_id, stripe_subscription_id, status, now, user_id))
    else:
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, stripe_customer_id, stripe_subscription_id, status, week_reset_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, plan, stripe_customer_id, stripe_subscription_id, status, now))

    conn.commit()
    conn.close()
    return get_subscription(user_id)


def increment_scan_count(user_id: int) -> int:
    """Increment scans_this_week counter. Resets if a new week has started. Returns new count."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, scans_this_week, week_reset_at)
            VALUES (?, 'free', 1, ?)
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
    cursor.execute("""
        UPDATE subscriptions SET scans_this_week=?, week_reset_at=?, updated_at=?
        WHERE user_id=?
    """, (new_count, week_reset_at, now_iso, user_id))
    conn.commit()
    conn.close()
    return new_count


# Initialize database on import
init_db()
