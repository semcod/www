"""Celery worker configuration - async task processing for Semcod."""
import os
from celery import Celery
from typing import Dict, Any

# Redis broker from env or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery = Celery(
    "semcod",
    broker=REDIS_URL,
    backend=None,  # Disable result backend to avoid Redis connection issues
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
    task_track_started=False,  # Disable tracking to avoid backend connection
    task_time_limit=300,  # 5 min timeout
    worker_prefetch_multiplier=1,  # Fair task distribution
    # Result backend settings
    result_expires=3600,  # 1 hour result retention
    # Retry settings
    task_default_retry_delay=60,  # 1 min between retries
    task_max_retries=3,
)


def get_celery_app() -> Celery:
    """Get configured Celery application instance."""
    return celery
