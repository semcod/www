"""Database schema initialization."""

import sqlite3
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

    # ─── SaaS Multi-tenancy Tables ─────────────────────────────────────────────

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            provider_user_id TEXT NOT NULL,
            login TEXT NOT NULL,
            name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            plan TEXT DEFAULT 'free',
            billing_customer_id TEXT DEFAULT '',
            billing_subscription_id TEXT DEFAULT '',
            usage_limits TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(provider, provider_user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            UNIQUE(tenant_id, provider, full_name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS installations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            last_scan_score INTEGER DEFAULT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            FOREIGN KEY (repository_id) REFERENCES repositories (id),
            UNIQUE(tenant_id, repository_id)
        )
    """)

    # ─── Event Queue Table ──────────────────────────────────────────────────────

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()
