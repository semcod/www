"""Celery tasks package - re-exports all task modules."""

from .scan import (
    run_audit,
    process_pr_event,
    process_push_event,
    analyze_diff,
    _format_pr_comment,
    _get_token_for_provider,
)
from .autopr import (
    create_auto_pr,
    create_auto_fix_pr,
)
from .maintenance import (
    check_health_regression,
    check_score_and_notify,
)
from .marketplace import (
    sync_mirror_task,
    schedule_periodic_mirrors,
)
from .redsl import (
    task_redsl_analyze,
    task_redsl_refactor,
    task_redsl_health_check,
    task_redsl_scheduled_quality_check,
    task_redsl_scheduled_auto_refactor,
)
from .quality_loop import (
    task_on_push_quality_loop,
)

# Re-export all tasks for backward compatibility
__all__ = [
    "run_audit",
    "process_pr_event",
    "process_push_event",
    "analyze_diff",
    "_format_pr_comment",
    "_get_token_for_provider",
    "create_auto_pr",
    "create_auto_fix_pr",
    "check_health_regression",
    "check_score_and_notify",
    "sync_mirror_task",
    "schedule_periodic_mirrors",
    "task_redsl_analyze",
    "task_redsl_refactor",
    "task_redsl_health_check",
    "task_redsl_scheduled_quality_check",
    "task_redsl_scheduled_auto_refactor",
    "task_on_push_quality_loop",
]
