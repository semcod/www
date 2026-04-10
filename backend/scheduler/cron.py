"""APScheduler setup + REST API for managing scan schedules."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from scheduler.scan_job import run_scheduled_scan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/schedules", tags=["scheduler"])

# ─── In-process scheduler (singleton) ─────────────────────────────────────────

_scheduler = AsyncIOScheduler()
_schedules: Dict[str, dict] = {}  # repo → schedule metadata


def get_scheduler() -> AsyncIOScheduler:
    return _scheduler


def start_scheduler() -> None:
    if not _scheduler.running:
        _scheduler.start()
        logger.info("APScheduler started")


def stop_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")


# ─── Pydantic models ───────────────────────────────────────────────────────────

class ScheduleCreate(BaseModel):
    repo: str = Field(..., description="owner/repo")
    interval_hours: float = Field(1.0, ge=0.1, le=168, description="Scan interval in hours")
    token: str = Field("", description="GitHub token (empty = public repo)")
    webhook_url: str | None = Field(None, description="Slack/Discord webhook for degradation alerts")


class ScheduleOut(BaseModel):
    repo: str
    interval_hours: float
    next_run: str | None
    created_at: str
    webhook_url: str | None


# ─── Internal helpers ──────────────────────────────────────────────────────────

def _job_id(repo: str) -> str:
    return f"scan:{repo.replace('/', ':')}"


def _next_run_iso(job_id: str) -> str | None:
    job = _scheduler.get_job(job_id)
    if job and job.next_run_time:
        return job.next_run_time.isoformat()
    return None


def _run_scan_sync(repo: str, token: str, webhook_url: str | None) -> None:
    """Wrapper called by APScheduler (sync) — launches the async job."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(run_scheduled_scan(repo, token, webhook_url))


# ─── API endpoints ─────────────────────────────────────────────────────────────

@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(body: ScheduleCreate) -> ScheduleOut:
    """Register a new periodic scan for a repository."""
    job_id = _job_id(body.repo)

    if _scheduler.get_job(job_id):
        raise HTTPException(409, f"Schedule already exists for {body.repo}. Use PATCH to update.")

    _scheduler.add_job(
        _run_scan_sync,
        trigger=IntervalTrigger(hours=body.interval_hours),
        id=job_id,
        args=[body.repo, body.token, body.webhook_url],
        replace_existing=False,
    )

    _schedules[body.repo] = {
        "repo": body.repo,
        "interval_hours": body.interval_hours,
        "token": body.token,
        "webhook_url": body.webhook_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("Schedule created: %s every %.1fh", body.repo, body.interval_hours)
    return ScheduleOut(
        repo=body.repo,
        interval_hours=body.interval_hours,
        next_run=_next_run_iso(job_id),
        created_at=_schedules[body.repo]["created_at"],
        webhook_url=body.webhook_url,
    )


@router.get("", response_model=List[ScheduleOut])
async def list_schedules() -> List[ScheduleOut]:
    """List all active scan schedules."""
    result = []
    for repo, meta in _schedules.items():
        result.append(ScheduleOut(
            repo=repo,
            interval_hours=meta["interval_hours"],
            next_run=_next_run_iso(_job_id(repo)),
            created_at=meta["created_at"],
            webhook_url=meta.get("webhook_url"),
        ))
    return result


@router.get("/{owner}/{repo}", response_model=ScheduleOut)
async def get_schedule(owner: str, repo: str) -> ScheduleOut:
    """Get schedule details for a specific repository."""
    full_repo = f"{owner}/{repo}"
    if full_repo not in _schedules:
        raise HTTPException(404, f"No schedule found for {full_repo}")
    meta = _schedules[full_repo]
    return ScheduleOut(
        repo=full_repo,
        interval_hours=meta["interval_hours"],
        next_run=_next_run_iso(_job_id(full_repo)),
        created_at=meta["created_at"],
        webhook_url=meta.get("webhook_url"),
    )


@router.patch("/{owner}/{repo}", response_model=ScheduleOut)
async def update_schedule(owner: str, repo: str, body: ScheduleCreate) -> ScheduleOut:
    """Update interval or webhook for an existing schedule."""
    full_repo = f"{owner}/{repo}"
    job_id = _job_id(full_repo)

    if not _scheduler.get_job(job_id):
        raise HTTPException(404, f"No schedule found for {full_repo}")

    _scheduler.reschedule_job(job_id, trigger=IntervalTrigger(hours=body.interval_hours))
    _schedules[full_repo]["interval_hours"] = body.interval_hours
    _schedules[full_repo]["webhook_url"] = body.webhook_url

    logger.info("Schedule updated: %s every %.1fh", full_repo, body.interval_hours)
    meta = _schedules[full_repo]
    return ScheduleOut(
        repo=full_repo,
        interval_hours=meta["interval_hours"],
        next_run=_next_run_iso(job_id),
        created_at=meta["created_at"],
        webhook_url=meta.get("webhook_url"),
    )


@router.delete("/{owner}/{repo}", status_code=204)
async def delete_schedule(owner: str, repo: str) -> None:
    """Remove a scheduled scan."""
    full_repo = f"{owner}/{repo}"
    job_id = _job_id(full_repo)

    if not _scheduler.get_job(job_id):
        raise HTTPException(404, f"No schedule found for {full_repo}")

    _scheduler.remove_job(job_id)
    _schedules.pop(full_repo, None)
    logger.info("Schedule removed: %s", full_repo)
