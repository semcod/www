"""Session-aware wrapper functions for backward compatibility.

All 37 wrappers follow the same pattern: open a session, delegate to the ORM
function, close the session. The ``_wrap`` factory encodes that pattern once.
Public API is identical to the original hand-written wrappers.
"""
from functools import wraps

from db_session import SessionLocal
from .scans_orm import (
    save_scan as save_scan_orm,
    get_recent_scans as get_recent_scans_orm,
    get_repo_scans as get_repo_scans_orm,
    get_total_scan_count as get_total_scan_count_orm,
    save_audit_result as save_audit_result_orm,
    get_audit_result as get_audit_result_orm,
    save_badge_cache as save_badge_cache_orm,
    get_badge_cache as get_badge_cache_orm,
)
from .users_orm import (
    upsert_user as upsert_user_orm,
    get_user_by_github_id as get_user_by_github_id_orm,
    get_user_by_id as get_user_by_id_orm,
    get_subscription as get_subscription_orm,
    upsert_subscription as upsert_subscription_orm,
    increment_scan_count as increment_scan_count_orm,
)
from .tenants_orm import (
    get_or_create_tenant as get_or_create_tenant_orm,
    get_tenant_by_id as get_tenant_by_id_orm,
    update_tenant_plan as update_tenant_plan_orm,
)
from .repositories_orm import (
    get_or_create_repository as get_or_create_repository_orm,
    get_tenant_repositories as get_tenant_repositories_orm,
    get_repository_by_full_name as get_repository_by_full_name_orm,
)
from .installations_orm import (
    create_installation as create_installation_orm,
    get_installation as get_installation_orm,
    get_tenant_installations as get_tenant_installations_orm,
    delete_installation as delete_installation_orm,
    update_installation_scan as update_installation_scan_orm,
)
from .events_orm import (
    queue_event as queue_event_orm,
    get_pending_events as get_pending_events_orm,
    update_event_status as update_event_status_orm,
)
from .benchmark_orm import (
    create_benchmark_case as create_benchmark_case_orm,
    get_benchmark_cases as get_benchmark_cases_orm,
    get_benchmark_case as get_benchmark_case_orm,
    update_benchmark_case as update_benchmark_case_orm,
    create_benchmark_event as create_benchmark_event_orm,
    get_benchmark_events as get_benchmark_events_orm,
    upsert_recommendation_feedback as upsert_recommendation_feedback_orm,
    get_feedback_for_case as get_feedback_for_case_orm,
    get_benchmark_summary as get_benchmark_summary_orm,
)


def _wrap(orm_fn):
    """Wrap an ORM function (db, *args) → SessionLocal-managed call."""
    @wraps(orm_fn)
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return orm_fn(db, *args, **kwargs)
        finally:
            db.close()
    wrapper.__name__ = orm_fn.__name__.removesuffix("_orm")
    return wrapper


# ─── Public API (identical signatures to the original hand-written wrappers) ──

save_scan                   = _wrap(save_scan_orm)
get_recent_scans            = _wrap(get_recent_scans_orm)
get_repo_scans              = _wrap(get_repo_scans_orm)
get_total_scan_count        = _wrap(get_total_scan_count_orm)
save_audit_result           = _wrap(save_audit_result_orm)
get_audit_result            = _wrap(get_audit_result_orm)
save_badge_cache            = _wrap(save_badge_cache_orm)
get_badge_cache             = _wrap(get_badge_cache_orm)

upsert_user                 = _wrap(upsert_user_orm)
get_user_by_github_id       = _wrap(get_user_by_github_id_orm)
get_user_by_id              = _wrap(get_user_by_id_orm)
get_subscription            = _wrap(get_subscription_orm)
upsert_subscription         = _wrap(upsert_subscription_orm)
increment_scan_count        = _wrap(increment_scan_count_orm)

get_or_create_tenant        = _wrap(get_or_create_tenant_orm)
get_tenant_by_id            = _wrap(get_tenant_by_id_orm)
update_tenant_plan          = _wrap(update_tenant_plan_orm)

get_or_create_repository    = _wrap(get_or_create_repository_orm)
get_tenant_repositories     = _wrap(get_tenant_repositories_orm)
get_repository_by_full_name = _wrap(get_repository_by_full_name_orm)

create_installation         = _wrap(create_installation_orm)
get_installation            = _wrap(get_installation_orm)
get_tenant_installations    = _wrap(get_tenant_installations_orm)
delete_installation         = _wrap(delete_installation_orm)
update_installation_scan    = _wrap(update_installation_scan_orm)

queue_event                 = _wrap(queue_event_orm)
get_pending_events          = _wrap(get_pending_events_orm)
update_event_status         = _wrap(update_event_status_orm)

create_benchmark_case       = _wrap(create_benchmark_case_orm)
get_benchmark_cases         = _wrap(get_benchmark_cases_orm)
get_benchmark_case          = _wrap(get_benchmark_case_orm)
update_benchmark_case       = _wrap(update_benchmark_case_orm)
create_benchmark_event      = _wrap(create_benchmark_event_orm)
get_benchmark_events        = _wrap(get_benchmark_events_orm)
upsert_recommendation_feedback = _wrap(upsert_recommendation_feedback_orm)
get_feedback_for_case       = _wrap(get_feedback_for_case_orm)
get_benchmark_summary       = _wrap(get_benchmark_summary_orm)
