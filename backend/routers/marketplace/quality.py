"""Marketplace quality report — health score for marketplace listings."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db_module.wrappers import get_repo_scans, get_badge_cache

logger = logging.getLogger(__name__)

router = APIRouter(tags=["marketplace"])


class QualityReport(BaseModel):
    grade: str = "?"
    score: Optional[int] = None
    badge_url: str = ""
    dimensions: Dict[str, Any] = {}
    last_audit: Optional[str] = None
    auto_maintained: bool = False
    scan_count: int = 0
    trend: str = "stable"


@router.get("/marketplace/{owner}/{repo}/quality", response_model=QualityReport)
async def marketplace_quality(owner: str, repo: str) -> QualityReport:
    """Quality report for a marketplace listing.

    Buyers see: "This project has health A+ (score 96)"
    """
    full_repo = f"{owner}/{repo}"

    # Try badge cache first (fastest)
    cached = get_badge_cache(full_repo)
    if cached:
        return QualityReport(
            grade=cached.get("grade", "?"),
            score=cached.get("score"),
            badge_url=f"/badge/{full_repo.replace('/', '-')}.svg",
            last_audit=cached.get("updated"),
            scan_count=1,
        )

    # Fall back to scan history
    scans = get_repo_scans(full_repo, limit=10)
    if not scans:
        raise HTTPException(404, f"No quality data for {full_repo}")

    latest = scans[-1]  # scans ordered ASC, last is most recent
    score = latest["health_score"]
    grade = latest["grade"]

    # Compute trend
    trend = "stable"
    if len(scans) >= 2:
        prev_score = scans[-2]["health_score"]
        delta = score - prev_score
        if delta >= 3:
            trend = "improving"
        elif delta <= -3:
            trend = "degrading"

    return QualityReport(
        grade=grade,
        score=score,
        badge_url=f"/badge/{full_repo.replace('/', '-')}.svg",
        dimensions=latest.get("stats", {}),
        last_audit=latest.get("completed"),
        scan_count=len(scans),
        trend=trend,
    )
