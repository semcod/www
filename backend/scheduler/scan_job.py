"""Scheduled scan job — clones repo, runs analysis, persists result, fires alerts."""

import asyncio
import hashlib
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from config import APP_URL
from db_module.scans import get_repo_scans, save_scan
from services.analyzer import count_code_stats, run_tool
from services.scoring import calculate_health_score, generate_recommendations, score_to_grade
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
        logger.warning("Degradation alert for %s but no webhook configured: %s", alert["repo"], alert)
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


async def run_scheduled_scan(repo: str, token: str = "", webhook_url: str | None = None) -> dict:
    """
    Execute a full audit pipeline for *repo* (scheduled, no HTTP context).

    Returns the completed scan entry dict (same shape as save_scan input).
    token may be empty for public repos (shallow clone without auth).
    """
    audit_id = _build_audit_id(repo)
    audit_results[audit_id] = {"status": "running", "repo": repo, "started": _utc_now_iso()}

    workdir = Path(tempfile.mkdtemp(prefix="semcod-sched-"))
    try:
        clone_url = (
            f"https://x-access-token:{token}@github.com/{repo}.git"
            if token
            else f"https://github.com/{repo}.git"
        )
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth=1", clone_url, str(workdir / "repo"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"git clone failed for {repo}")

        repo_path = workdir / "repo"
        stats = await count_code_stats(repo_path)

        code2llm_result = await run_tool(
            "code2llm",
            ["analyze", str(repo_path), "--format", "json"],
            fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0},
        )
        redup_result = await run_tool(
            "redup",
            ["scan", str(repo_path), "--format", "json"],
            fallback={"duplication_groups": 0, "duplicated_lines": 0, "recoverable_lines": 0},
        )
        pyqual_result = await run_tool(
            "pyqual",
            ["check", str(repo_path), "--format", "json"],
            fallback={"passed": 0, "warnings": 0, "errors": 0, "score": 0},
        )

        health_score = calculate_health_score(stats, code2llm_result, redup_result, pyqual_result)
        recommendations = generate_recommendations(code2llm_result, redup_result, pyqual_result)

        scan_entry = {
            "repo": repo,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "stats": stats,
            "completed": _utc_now_iso(),
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }

        audit_results[audit_id] = {
            "status": "complete",
            **scan_entry,
            "metrics": {
                "complexity": code2llm_result,
                "duplication": redup_result,
                "quality": pyqual_result,
            },
            "recommendations": recommendations,
        }

        badge_cache[repo] = {
            "score": health_score,
            "grade": score_to_grade(health_score),
            "updated": _utc_now_iso(),
            "weekly_issues": sum(1 for r in recommendations if r.get("priority") in ("high", "medium")),
        }

        scan_history.insert(0, scan_entry)

        try:
            save_scan(scan_entry)
        except Exception as exc:
            logger.error("Failed to persist scan for %s: %s", repo, exc)

        alert = _detect_degradation(repo, health_score)
        if alert:
            await _fire_alert(alert, webhook_url)

        logger.info("Scheduled scan complete: %s score=%d", repo, health_score)
        return scan_entry

    except Exception as exc:
        audit_results[audit_id] = {"status": "error", "repo": repo, "error": str(exc)}
        logger.error("Scheduled scan failed for %s: %s", repo, exc)
        raise
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
