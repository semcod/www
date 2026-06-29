"""Quality loop — auto-trigger reDSL analysis + refactor + PR on push events."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

try:
    from celery import shared_task

    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task  # type: ignore[assignment]

logger = logging.getLogger(__name__)

_HEALTH_THRESHOLD = 70  # trigger refactor below this
_AUTO_PR_MAX_ACTIONS = 3


@shared_task(bind=True, max_retries=2)
def task_on_push_quality_loop(
    self,
    repo: str,
    commit_sha: str,
    project_path: str,
    token: str = "",
    provider: str = "github",
) -> Dict[str, Any]:
    """Full quality loop triggered by a push webhook.

    1. Health check via reDSL
    2. Save health snapshot
    3. If health < threshold → create ticket + refactor + PR
    """

    loop = _get_loop()
    try:
        return loop.run_until_complete(
            _run_quality_loop(repo, commit_sha, project_path, token, provider)
        )
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120)
        logger.error("quality_loop failed for %s: %s", repo, exc)
        return {"status": "failed", "repo": repo, "error": str(exc)}


async def _run_quality_loop(
    repo: str,
    commit_sha: str,
    project_path: str,
    token: str,
    provider: str,
) -> Dict[str, Any]:
    """Async implementation of the quality loop."""
    from services.redsl_client import RedslClient

    redsl = RedslClient()

    # 1. Check if reDSL is available
    if not await redsl.health():
        logger.warning("reDSL unavailable — skipping quality loop for %s", repo)
        return {"status": "skipped", "reason": "redsl_unavailable", "repo": repo}

    # 2. Get health score
    health = await redsl.health_score(project_path)
    score = health.get("score", 100)
    grade = health.get("grade", "?")

    # 3. Save health snapshot to DB
    _save_health_snapshot(repo, health, commit_sha)

    # 4. Check for health drop vs previous snapshot
    _check_health_drop(repo, score)

    # 5. If health is above threshold, nothing more to do
    if score >= _HEALTH_THRESHOLD:
        logger.info("quality_loop: %s health=%d (%s) — OK", repo, score, grade)
        return {
            "status": "healthy",
            "repo": repo,
            "score": score,
            "grade": grade,
        }

    # 6. Create auto-ticket
    ticket_id = _create_quality_ticket(repo, health)
    logger.info(
        "quality_loop: %s health=%d — created ticket %s", repo, score, ticket_id
    )

    # 7. Run reDSL cycle (analyze + apply refactoring)
    try:
        cycle_result = await redsl.cycle(
            project_path=project_path,
            max_actions=_AUTO_PR_MAX_ACTIONS,
            clear_history=True,
        )
    except Exception as exc:
        logger.error("quality_loop cycle failed for %s: %s", repo, exc)
        _update_ticket_error(ticket_id, str(exc))
        return {
            "status": "cycle_failed",
            "repo": repo,
            "score": score,
            "ticket_id": ticket_id,
            "error": str(exc),
        }

    proposals_applied = cycle_result.get("proposals_applied", 0)
    files_modified = cycle_result.get("files_modified", [])

    if proposals_applied == 0 and not files_modified:
        logger.info("quality_loop: %s — no changes to apply", repo)
        _update_ticket_status(ticket_id, "no_changes")
        return {
            "status": "no_changes",
            "repo": repo,
            "score": score,
            "ticket_id": ticket_id,
        }

    # 8. Create auto-PR if token available
    pr_url = None
    if token:
        pr_url = await _create_quality_pr(
            repo,
            project_path,
            token,
            provider,
            ticket_id,
            files_modified,
            score,
            grade,
        )

    _update_ticket_status(
        ticket_id,
        "pr_created" if pr_url else "refactored",
        pr_url=pr_url,
    )

    # 9. Update badge cache
    _update_badge_cache(repo, health)

    return {
        "status": "pr_created" if pr_url else "refactored",
        "repo": repo,
        "score": score,
        "grade": grade,
        "ticket_id": ticket_id,
        "proposals_applied": proposals_applied,
        "files_modified": files_modified,
        "pr_url": pr_url,
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _get_loop():
    """Get or create an asyncio event loop."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def _save_health_snapshot(repo: str, health: dict, commit_sha: str) -> None:
    """Persist a health snapshot to the scans DB."""
    try:
        from db_module.wrappers import save_scan, save_badge_cache
        from config import APP_URL

        now = datetime.now(timezone.utc).isoformat()
        scan_entry = {
            "repo": repo,
            "health_score": health.get("score", 0),
            "grade": health.get("grade", "?"),
            "stats": health.get("dimensions", {}),
            "completed": now,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }
        save_scan(scan_entry)

        save_badge_cache(
            repo,
            {
                "score": health.get("score", 0),
                "grade": health.get("grade", "?"),
                "updated": now,
                "weekly_issues": None,
            },
        )
    except Exception as exc:
        logger.warning("Failed to save health snapshot for %s: %s", repo, exc)


def _check_health_drop(repo: str, current_score: int) -> None:
    """Alert if health dropped ≥5 points vs previous scan."""
    try:
        from db_module.wrappers import get_repo_scans

        scans = get_repo_scans(repo, limit=2)
        if len(scans) < 2:
            return
        prev_score = scans[-2]["health_score"]
        delta = current_score - prev_score
        if delta <= -5:
            logger.warning(
                "Health drop for %s: %d → %d (%+d)",
                repo,
                prev_score,
                current_score,
                delta,
            )
    except Exception as exc:
        logger.warning("Failed to check health drop for %s: %s", repo, exc)


def _create_quality_ticket(repo: str, health: dict) -> str:
    """Create an auto-generated quality ticket. Returns ticket_id."""
    try:
        from db_module.tickets_orm import create_ticket

        score = health.get("score", 0)
        grade = health.get("grade", "?")
        priority = "high" if score < 50 else "medium"
        dims = health.get("dimensions", {})
        description = (
            f"Automated quality ticket — health score {score} ({grade}).\n\n"
            f"Dimensions: {dims}\n\n"
            f"Triggered by push webhook."
        )
        ticket = create_ticket(
            title=f"Auto: improve {repo} health ({grade}, score={score})",
            repo=repo,
            priority=priority,
            description=description,
        )
        return ticket.get("id", ticket.get("ticket_id", "unknown"))
    except Exception as exc:
        logger.warning("Failed to create quality ticket for %s: %s", repo, exc)
        return "unknown"


def _update_ticket_status(
    ticket_id: str, status: str, pr_url: str | None = None
) -> None:
    """Update ticket status."""
    try:
        from db_module.tickets_orm import update_ticket
        from db_session import SessionLocal

        updates = {"status": status}
        if pr_url:
            updates["pr_url"] = pr_url
        db = SessionLocal()
        try:
            update_ticket(db, ticket_id, updates)
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Failed to update ticket %s: %s", ticket_id, exc)


def _update_ticket_error(ticket_id: str, error: str) -> None:
    """Mark ticket as errored."""
    try:
        from db_module.tickets_orm import mark_ticket_error
        from db_session import SessionLocal

        db = SessionLocal()
        try:
            mark_ticket_error(db, ticket_id, error)
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Failed to mark ticket %s error: %s", ticket_id, exc)


async def _create_quality_pr(
    repo: str,
    project_path: str,
    token: str,
    provider: str,
    ticket_id: str,
    files_modified: list[str],
    score: int,
    grade: str,
) -> str | None:
    """Create a PR from reDSL refactoring results. Returns PR URL or None."""
    try:
        from worker.tasks.autopr import create_auto_pr

        branch = f"semcod-quality-{ticket_id[:8]}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

        patches = []
        for file_path in files_modified:
            full_path = f"{project_path}/{file_path}"
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                patches.append({"path": file_path, "content": content})
            except Exception:
                continue

        if not patches:
            return None

        result = create_auto_pr.delay(
            repo=repo,
            base_branch="main",
            patches=patches,
            proposal_type=f"quality-{ticket_id[:8]}",
            llm_prompt=f"Auto quality improvement: health {score} ({grade})",
            token=token,
            provider_type=provider,
        )
        # Result contains PR URL when task completes
        return getattr(result, "pr_url", None)
    except Exception as exc:
        logger.error("Failed to create quality PR for %s: %s", repo, exc)
        return None


def _update_badge_cache(repo: str, health: dict) -> None:
    """Update in-memory badge cache."""
    try:
        from store import badge_cache

        badge_cache[repo] = {
            "score": health.get("score", 0),
            "grade": health.get("grade", "?"),
            "updated": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.warning("Failed to update badge cache for %s: %s", repo, exc)
