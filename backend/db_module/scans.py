"""Scan-related database operations."""

import sqlite3
import json
from typing import List, Dict
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
        return conn


def save_scan(scan_data: Dict) -> int:
    """Save a scan to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(f"""
        INSERT INTO scans (repo, health_score, grade, stats, completed, sandbox, badge_url)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
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
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(f"""
        SELECT repo, health_score, grade, stats, completed, sandbox, badge_url
        FROM scans
        ORDER BY created_at DESC
        LIMIT {placeholder}
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
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(f"""
        SELECT repo, health_score, grade, stats, completed, sandbox, badge_url
        FROM scans
        WHERE repo = {placeholder}
        ORDER BY created_at ASC
        LIMIT {placeholder}
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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scans")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def save_audit_result(audit_id: str, audit_data: Dict) -> None:
    """Save audit result to database."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            INSERT INTO audit_results (audit_id, repo, status, started, completed, health_score, grade, stats, metrics, recommendations, error)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (audit_id) DO UPDATE SET
                repo = EXCLUDED.repo,
                status = EXCLUDED.status,
                started = EXCLUDED.started,
                completed = EXCLUDED.completed,
                health_score = EXCLUDED.health_score,
                grade = EXCLUDED.grade,
                stats = EXCLUDED.stats,
                metrics = EXCLUDED.metrics,
                recommendations = EXCLUDED.recommendations,
                error = EXCLUDED.error
        """, (
            audit_id,
            audit_data.get("repo"),
            audit_data.get("status"),
            audit_data.get("started"),
            audit_data.get("completed"),
            audit_data.get("health_score"),
            audit_data.get("grade"),
            json.dumps(audit_data.get("stats", {})),
            json.dumps(audit_data.get("metrics", {})),
            json.dumps(audit_data.get("recommendations", [])),
            audit_data.get("error"),
        ))
    else:
        placeholder = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"""
            INSERT OR REPLACE INTO audit_results (audit_id, repo, status, started, completed, health_score, grade, stats, metrics, recommendations, error)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """, (
            audit_id,
            audit_data.get("repo"),
            audit_data.get("status"),
            audit_data.get("started"),
            audit_data.get("completed"),
            audit_data.get("health_score"),
            audit_data.get("grade"),
            json.dumps(audit_data.get("stats", {})),
            json.dumps(audit_data.get("metrics", {})),
            json.dumps(audit_data.get("recommendations", [])),
            audit_data.get("error"),
        ))

    conn.commit()
    conn.close()


def get_audit_result(audit_id: str) -> Dict | None:
    """Get audit result from database."""
    conn = get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if USE_POSTGRES else "?"
    cursor.execute(f"""
        SELECT audit_id, repo, status, started, completed, health_score, grade, stats, metrics, recommendations, error
        FROM audit_results
        WHERE audit_id = {placeholder}
    """, (audit_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "audit_id": row["audit_id"],
        "repo": row["repo"],
        "status": row["status"],
        "started": row["started"],
        "completed": row["completed"],
        "health_score": row["health_score"],
        "grade": row["grade"],
        "stats": json.loads(row["stats"]) if row["stats"] else {},
        "metrics": json.loads(row["metrics"]) if row["metrics"] else {},
        "recommendations": json.loads(row["recommendations"]) if row["recommendations"] else [],
        "error": row["error"],
    }


def save_badge_cache(repo: str, badge_data: Dict) -> None:
    """Save badge cache to database."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            INSERT INTO badge_cache (repo, score, grade, updated, weekly_issues)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (repo) DO UPDATE SET
                score = EXCLUDED.score,
                grade = EXCLUDED.grade,
                updated = EXCLUDED.updated,
                weekly_issues = EXCLUDED.weekly_issues
        """, (
            repo,
            badge_data.get("score"),
            badge_data.get("grade"),
            badge_data.get("updated"),
            badge_data.get("weekly_issues"),
        ))
    else:
        cursor.execute("""
            INSERT OR REPLACE INTO badge_cache (repo, score, grade, updated, weekly_issues)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            repo,
            badge_data.get("score"),
            badge_data.get("grade"),
            badge_data.get("updated"),
            badge_data.get("weekly_issues"),
        ))

    conn.commit()
    conn.close()


def get_badge_cache(repo: str) -> Dict | None:
    """Get badge cache from database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT repo, score, grade, updated, weekly_issues
        FROM badge_cache
        WHERE repo = %s
    """, (repo,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "repo": row["repo"],
        "score": row["score"],
        "grade": row["grade"],
        "updated": row["updated"],
        "weekly_issues": row["weekly_issues"],
    }
