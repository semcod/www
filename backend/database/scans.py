"""Scan-related database operations."""

import sqlite3
import json
from typing import List, Dict
from config import DB_PATH


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
