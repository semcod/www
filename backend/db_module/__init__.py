"""SQLite database for scan history persistence."""

from .scans import (
    save_scan,
    get_recent_scans,
    get_repo_scans,
    get_total_scan_count,
    save_audit_result,
    get_audit_result,
    save_badge_cache,
    get_badge_cache,
)
from .users import (
    upsert_user,
    get_user_by_github_id,
    get_user_by_id,
    get_subscription,
    upsert_subscription,
    increment_scan_count,
)
from .tenants import (
    get_or_create_tenant,
    get_tenant_by_id,
    update_tenant_plan,
)
from .repositories import (
    get_or_create_repository,
    get_tenant_repositories,
    get_repository_by_full_name,
)
from .installations import (
    create_installation,
    get_installation,
    get_tenant_installations,
    delete_installation,
    update_installation_scan,
)
from .events import (
    queue_event,
    get_pending_events,
    update_event_status,
)
from .schema import init_db
from config import DB_TYPE

def convert_params(query, params):
    """Convert query parameters based on database type.
    
    SQLite uses ? placeholders, PostgreSQL uses %s placeholders.
    This function converts the query and params accordingly.
    """
    if DB_TYPE == "postgresql":
        # Replace ? with %s for PostgreSQL
        query = query.replace("?", "%s")
    return query, params

__all__ = [
    "init_db",
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
