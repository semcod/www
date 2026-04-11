"""Database schema initialization."""

import sqlite3
from config import DB_PATH
from .db_connection import get_connection, USE_POSTGRES


def init_db():
    """Initialize the database and create tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # SQLite-specific optimizations
    if not USE_POSTGRES:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")

    # Use SERIAL for PostgreSQL, AUTOINCREMENT for SQLite
    id_type = "SERIAL" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS scans (
            id {id_type},
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

    # Use SERIAL for PostgreSQL, AUTOINCREMENT for SQLite
    id_type = "SERIAL" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id {id_type},
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

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            github_id INTEGER UNIQUE NOT NULL,
            login TEXT NOT NULL,
            name TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            github_token TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ─── SaaS Multi-tenancy Tables ─────────────────────────────────────────────

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS tenants (
            id {id_type},
            provider TEXT NOT NULL,
            provider_user_id TEXT NOT NULL,
            login TEXT NOT NULL,
            name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            plan TEXT DEFAULT 'free',
            billing_customer_id TEXT DEFAULT '',
            billing_subscription_id TEXT DEFAULT '',
            usage_limits TEXT DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(provider, provider_user_id)
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS repositories (
            id {id_type},
            tenant_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            repo_provider_id TEXT NOT NULL,
            name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            private INTEGER DEFAULT 0,
            default_branch TEXT DEFAULT 'main',
            web_url TEXT DEFAULT '',
            clone_url TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS installations (
            id {id_type},
            tenant_id INTEGER NOT NULL,
            repository_id INTEGER NOT NULL,
            apps TEXT DEFAULT '[]',
            webhook_id TEXT DEFAULT '',
            webhook_secret TEXT DEFAULT '',
            webhook_url TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_scan_at TIMESTAMP DEFAULT NULL,
            last_scan_score INTEGER DEFAULT NULL
        )
    """)

    # ─── Event Queue Table ──────────────────────────────────────────────────────

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS events (
            id {id_type},
            event_id TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            provider TEXT NOT NULL,
            repo_full_name TEXT NOT NULL,
            pr_id INTEGER DEFAULT NULL,
            payload TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            retry_count INTEGER DEFAULT 0,
            error_message TEXT DEFAULT '',
            processed_at TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ─── Event Queue Indexes ───────────────────────────────────────────────────

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events (type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_provider ON events (provider)")

    # ─── Audit Results Table ─────────────────────────────────────────────────────

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS audit_results (
            audit_id TEXT PRIMARY KEY,
            repo TEXT NOT NULL,
            status TEXT NOT NULL,
            started TEXT,
            completed TEXT,
            health_score INTEGER,
            grade TEXT,
            stats TEXT,
            metrics TEXT,
            recommendations TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_results_repo ON audit_results (repo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_results_status ON audit_results (status)")

    # ─── Badge Cache Table ───────────────────────────────────────────────────────

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS badge_cache (
            repo TEXT PRIMARY KEY,
            score INTEGER,
            grade TEXT,
            updated TEXT,
            weekly_issues INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
