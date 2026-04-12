"""Celery tasks for ReDSL autonomous refactoring."""

import asyncio
import logging
from typing import Dict, Any

try:
    from celery import shared_task
    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task  # type: ignore[assignment]

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def task_redsl_analyze(self, project_path: str, repo: str = "") -> Dict[str, Any]:
    """Background: run reDSL analysis and save results."""
    try:
        from services.redsl_client import RedslClient
        redsl = RedslClient()

        loop = _get_loop()
        result = loop.run_until_complete(redsl.analyze(project_path))

        # Save analysis to scans DB if repo provided
        if repo:
            _save_analysis(repo, result)

        # If health score < 50: schedule auto-refactor
        health = loop.run_until_complete(redsl.health_score(project_path))
        score = health.get("score", 100)
        if score < 50:
            task_redsl_refactor.delay(project_path, max_actions=3)

        return {"status": "analyzed", "repo": repo, "health_score": score}

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60)
        logger.error("redsl_analyze failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


@shared_task(bind=True, max_retries=2)
def task_redsl_refactor(self, project_path: str, max_actions: int = 5) -> Dict[str, Any]:
    """Background: run reDSL refactoring."""
    try:
        from services.redsl_client import RedslClient
        redsl = RedslClient()

        loop = _get_loop()
        result = loop.run_until_complete(
            redsl.refactor(project_path, max_actions=max_actions, dry_run=False, fmt="json")
        )

        proposals_applied = len(result.get("decisions", []))
        logger.info("redsl_refactor: %d proposals applied for %s", proposals_applied, project_path)

        return {"status": "refactored", "proposals_applied": proposals_applied, "result": result}

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120)
        logger.error("redsl_refactor failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


@shared_task(bind=True, max_retries=1)
def task_redsl_health_check(self, project_path: str) -> Dict[str, Any]:
    """Background: get health score for a project."""
    try:
        from services.redsl_client import RedslClient
        redsl = RedslClient()

        loop = _get_loop()
        result = loop.run_until_complete(redsl.health_score(project_path))
        return {"status": "ok", "health": result}

    except Exception as exc:
        logger.error("redsl_health_check failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


@shared_task
def task_redsl_scheduled_quality_check() -> Dict[str, Any]:
    """Scheduled: scan all repos with health < 70."""
    checked = 0
    refactored = 0

    try:
        repos = _get_repos_below_threshold(70)
        for repo_path in repos:
            task_redsl_analyze.delay(repo_path)
            checked += 1
    except Exception as exc:
        logger.error("scheduled_quality_check failed: %s", exc)

    return {"checked": checked, "refactored": refactored}


@shared_task
def task_redsl_scheduled_auto_refactor() -> Dict[str, Any]:
    """Scheduled weekly: auto-refactor up to 5 repos with health < 50."""
    refactored = 0

    try:
        repos = _get_repos_below_threshold(50)
        for repo_path in repos[:5]:
            task_redsl_refactor.delay(repo_path, max_actions=3)
            refactored += 1
    except Exception as exc:
        logger.error("scheduled_auto_refactor failed: %s", exc)

    return {"refactored": refactored}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_loop():
    """Get or create an asyncio event loop."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def _save_analysis(repo: str, result: dict) -> None:
    """Save reDSL analysis result to scans DB."""
    from datetime import datetime, timezone
    try:
        from db_module.wrappers import save_scan, save_badge_cache
        from config import APP_URL

        now = datetime.now(timezone.utc).isoformat()
        score = result.get("score", result.get("health_score", 0))
        grade = result.get("grade", "?")
        scan_entry = {
            "repo": repo,
            "health_score": score,
            "grade": grade,
            "stats": result.get("dimensions", result.get("stats", {})),
            "completed": now,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }
        save_scan(scan_entry)

        save_badge_cache(repo, {
            "score": score,
            "grade": grade,
            "updated": now,
            "weekly_issues": None,
        })

        # Check for health drop
        _check_health_drop(repo, score)
    except Exception as exc:
        logger.warning("Failed to save redsl analysis for %s: %s", repo, exc)


def _check_health_drop(repo: str, current_score: int) -> None:
    """Log warning if health dropped >=5 points vs previous scan."""
    try:
        from db_module.wrappers import get_repo_scans
        scans = get_repo_scans(repo, limit=2)
        if len(scans) < 2:
            return
        prev_score = scans[-2]["health_score"]
        delta = current_score - prev_score
        if delta <= -5:
            logger.warning(
                "HEALTH DROP for %s: %d → %d (%+d) — consider auto-refactor",
                repo, prev_score, current_score, delta,
            )
    except Exception as exc:
        logger.warning("Failed to check health drop for %s: %s", repo, exc)


def _get_repos_below_threshold(threshold: int) -> list[str]:
    """Get repos with health score below threshold."""
    try:
        from db_module.wrappers import get_recent_scans
        scans = get_recent_scans(limit=100)
        # Deduplicate: keep only most recent scan per repo
        seen: dict[str, int] = {}
        for s in scans:
            repo = s["repo"]
            if repo not in seen:
                seen[repo] = s.get("health_score", 100)
        return [repo for repo, score in seen.items() if score < threshold]
    except Exception:
        return []
