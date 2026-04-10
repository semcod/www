"""SQLite database for scan history persistence.

This module is a thin wrapper that re-exports all database functions
from the database package for backward compatibility.
"""

from db_module import (
    init_db,
    save_scan,
    get_recent_scans,
    get_repo_scans,
    get_total_scan_count,
    upsert_user,
    get_user_by_github_id,
    get_user_by_id,
    get_subscription,
    upsert_subscription,
    increment_scan_count,
    get_or_create_tenant,
    get_tenant_by_id,
    update_tenant_plan,
    get_or_create_repository,
    get_tenant_repositories,
    get_repository_by_full_name,
    create_installation,
    get_installation,
    get_tenant_installations,
    delete_installation,
    update_installation_scan,
    queue_event,
    get_pending_events,
    update_event_status,
    save_audit_result,
    get_audit_result,
    save_badge_cache,
    get_badge_cache,
)

__all__ = [
    "init_db",
    "save_scan",
    "get_recent_scans",
    "get_repo_scans",
    "get_total_scan_count",
    "upsert_user",
    "get_user_by_github_id",
    "get_user_by_id",
    "get_subscription",
    "upsert_subscription",
    "increment_scan_count",
    "get_or_create_tenant",
    "get_tenant_by_id",
    "update_tenant_plan",
    "get_or_create_repository",
    "get_tenant_repositories",
    "get_repository_by_full_name",
    "create_installation",
    "get_installation",
    "get_tenant_installations",
    "delete_installation",
    "update_installation_scan",
    "queue_event",
    "get_pending_events",
    "update_event_status",
    "save_audit_result",
    "get_audit_result",
    "save_badge_cache",
    "get_badge_cache",
]

# Initialize database on import
init_db()
