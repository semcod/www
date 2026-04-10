"""Maintenance Celery tasks - health checks and notifications."""
from typing import Dict, Any, Optional

try:
    from celery import shared_task
    from celery.exceptions import MaxRetriesExceededError
    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task, MaxRetriesExceededError  # type: ignore[assignment]


@shared_task
def check_health_regression(
    repo: str,
    previous_score: Optional[int],
    new_score: int,
    threshold: int = -5,
) -> Dict[str, Any]:
    """
    Check if health score regressed and create issue if needed.
    """
    if previous_score is None:
        return {"status": "no_baseline"}

    delta = new_score - previous_score

    if delta < threshold:
        return {
            "status": "regression_detected",
            "previous_score": previous_score,
            "new_score": new_score,
            "delta": delta,
            "should_alert": True,
        }

    return {
        "status": "ok",
        "delta": delta,
        "improvement": delta > 0,
    }


@shared_task
def check_score_and_notify(
    repo: str,
    previous_score: int,
    new_score: int,
    tenant_id: int,
    notification_webhook: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Check if score improved after auto-fix and send notifications.
    """
    from services.autofix import AutoFixService

    delta = new_score - previous_score

    result = {
        "repo": repo,
        "previous_score": previous_score,
        "new_score": new_score,
        "delta": delta,
        "improved": delta > 0,
    }

    # Send notification if configured
    if notification_webhook and delta < 0:
        # Score regressed - alert
        import httpx
        httpx.post(
            notification_webhook,
            json={
                "text": f"⚠️ Score regression in {repo}: {previous_score} → {new_score}",
            },
        )

    return result
