"""SQLAlchemy ORM database for scan history persistence."""

from db_session import SessionLocal, init_db as init_orm_db

# Import wrapper functions (session-aware, backward compatible)
from .wrappers import (
    save_scan,
    get_recent_scans,
    get_repo_scans,
    get_total_scan_count,
    save_audit_result,
    get_audit_result,
    save_badge_cache,
    get_badge_cache,
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
)

# Use ORM initialization
init_db = init_orm_db

__all__ = [
    "init_db",
    "SessionLocal",
    "save_scan",
    "get_recent_scans",
    "get_repo_scans",
    "get_total_scan_count",
    "save_audit_result",
    "get_audit_result",
    "save_badge_cache",
    "get_badge_cache",
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
]

# Initialize database on import
init_db()
