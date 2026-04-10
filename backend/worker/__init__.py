"""Worker module - Celery tasks for async processing."""
import os
from celery import Celery

# Redis broker from env or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery = Celery(
    "semcod",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker.tasks"],  # Tasks module
)

# Celery configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_track_started=True,
    task_time_limit=300,  # 5 min timeout
    worker_prefetch_multiplier=1,  # Fair task distribution
    # Result backend settings
    result_expires=3600,  # 1 hour result retention
    # Retry settings
    task_default_retry_delay=60,  # 1 min between retries
    task_max_retries=3,
)

from .tasks import (
    run_audit,
    process_pr_event,
    process_push_event,
    analyze_diff,
    create_auto_pr,
    check_health_regression,
)

__all__ = [
    "celery",
    "run_audit",
    "process_pr_event",
    "process_push_event",
    "analyze_diff",
    "create_auto_pr",
    "check_health_regression",
]
