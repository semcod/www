"""Scheduled scan job — clones repo, runs analysis, persists result, fires alerts."""

import hashlib
import logging
from datetime import datetime, timezone

from config import APP_URL
from db_module.wrappers import get_repo_scans, save_scan
from services.pipeline import run_pipeline
from store import audit_results, badge_cache, scan_history

logger = logging.getLogger(__name__)

DEGRADATION_THRESHOLD = 5  # points drop that triggers an alert


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_audit_id(repo: str) -> str:
    return hashlib.sha256(f"{repo}-{_utc_now_iso()}".encode()).hexdigest()[:12]


def _detect_degradation(repo: str, new_score: int) -> dict | None:
    """Return alert dict if health score dropped >= threshold vs last scan."""
    scans = get_repo_scans(repo, limit=2)
    if len(scans) < 2:
        return None
    prev_score = scans[-2]["health_score"]
    delta = new_score - prev_score
    if delta <= -DEGRADATION_THRESHOLD:
        return {
            "repo": repo,
            "prev_score": prev_score,
            "new_score": new_score,
            "delta": delta,
            "detected_at": _utc_now_iso(),
        }
    return None


async def _fire_alert(alert: dict, webhook_url: str | None) -> None:
    """POST degradation alert to webhook_url (Slack/Discord compatible)."""
    if not webhook_url:
        logger.warning(
            "Degradation alert for %s but no webhook configured: %s",
            alert["repo"],
            alert,
        )
        return

    import httpx

    payload = {
        "text": (
            f"⚠️ *Code health degradation detected*\n"
            f"Repo: `{alert['repo']}`\n"
            f"Score: {alert['prev_score']} → {alert['new_score']} ({alert['delta']:+d})"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(webhook_url, json=payload)
    except Exception as exc:
        logger.error("Failed to send alert for %s: %s", alert["repo"], exc)


async def run_scheduled_scan(
    repo: str, token: str = "", webhook_url: str | None = None
) -> dict:
    """
    Execute a full audit pipeline for *repo* (scheduled, no HTTP context).

    Returns the completed scan entry dict (same shape as save_scan input).
    token may be empty for public repos (shallow clone without auth).
    """
    audit_id = _build_audit_id(repo)
    audit_results[audit_id] = {
        "status": "running",
        "repo": repo,
        "started": _utc_now_iso(),
    }

    try:
        result = await run_pipeline(repo, token)

        scan_entry = {
            "repo": repo,
            "health_score": result.health_score,
            "grade": result.grade,
            "stats": result.stats,
            "completed": _utc_now_iso(),
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }

        audit_results[audit_id] = {
            "status": "complete",
            **scan_entry,
            "metrics": {
                "complexity": result.complexity,
                "duplication": result.duplication,
                "quality": result.quality,
            },
            "recommendations": result.recommendations,
        }

        badge_cache[repo] = {
            "score": result.health_score,
            "grade": result.grade,
            "updated": _utc_now_iso(),
            "weekly_issues": sum(
                1
                for r in result.recommendations
                if r.get("priority") in ("high", "medium")
            ),
        }

        scan_history.insert(0, scan_entry)

        try:
            save_scan(scan_entry)
        except Exception as exc:
            logger.error("Failed to persist scan for %s: %s", repo, exc)

        alert = _detect_degradation(repo, result.health_score)
        if alert:
            await _fire_alert(alert, webhook_url)

        logger.info("Scheduled scan complete: %s score=%d", repo, result.health_score)
        return scan_entry

    except Exception as exc:
        audit_results[audit_id] = {"status": "error", "repo": repo, "error": str(exc)}
        logger.error("Scheduled scan failed for %s: %s", repo, exc)
        raise
