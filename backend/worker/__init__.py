"""Worker module - Celery tasks for async processing."""
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    from celery import Celery as _Celery

    celery = _Celery(
        "semcod",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["worker.tasks"],
    )

    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_prefetch_multiplier=1,
        result_expires=3600,
        task_default_retry_delay=60,
        task_max_retries=3,
    )

    from .tasks import (
        run_audit,
        process_pr_event,
        process_push_event,
        analyze_diff,
        create_auto_pr,
        check_health_regression,
        task_on_push_quality_loop,
    )

except ImportError:  # celery not installed (e.g. test environment without Redis)
    celery = None  # type: ignore[assignment]

    from .tasks import (  # tasks define their own fallback stubs
        run_audit,
        process_pr_event,
        process_push_event,
        analyze_diff,
        create_auto_pr,
        check_health_regression,
        task_on_push_quality_loop,
    )

__all__ = [
    "celery",
    "run_audit",
    "process_pr_event",
    "process_push_event",
    "analyze_diff",
    "create_auto_pr",
    "check_health_regression",
    "task_on_push_quality_loop",
]
