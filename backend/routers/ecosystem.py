"""Ecosystem dashboard router — multi-project health overview."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from db_module.wrappers import get_recent_scans, get_repo_scans

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ecosystem", tags=["ecosystem"])


class ProjectHealth(BaseModel):
    name: str
    health_score: int | None = None
    grade: str = "?"
    trend: str = "stable"  # improving / stable / degrading
    last_scan: str | None = None
    scan_count: int = 0
    badge_url: str = ""


class EcosystemResponse(BaseModel):
    projects: List[ProjectHealth]
    priority_ranking: List[str]
    total_projects: int
    avg_health: float | None = None


@router.get("", response_model=EcosystemResponse)
async def get_ecosystem() -> EcosystemResponse:
    """Health score overview for all projects in the organization."""
    scans = get_recent_scans(limit=500)

    # Group scans by repo
    repo_scans: Dict[str, List[dict]] = {}
    for s in scans:
        repo_scans.setdefault(s["repo"], []).append(s)

    projects: List[ProjectHealth] = []
    for repo, scans_list in repo_scans.items():
        latest = scans_list[0]  # most recent (ordered by created_at DESC)
        score = latest["health_score"]

        # Compute trend from last 2 scans
        trend = "stable"
        if len(scans_list) >= 2:
            prev_score = scans_list[1]["health_score"]
            delta = score - prev_score
            if delta >= 3:
                trend = "improving"
            elif delta <= -3:
                trend = "degrading"

        projects.append(
            ProjectHealth(
                name=repo,
                health_score=score,
                grade=latest["grade"],
                trend=trend,
                last_scan=latest["completed"],
                scan_count=len(scans_list),
                badge_url=latest.get("badge_url", ""),
            )
        )

    # Sort by health score ascending (worst first = highest priority)
    projects.sort(key=lambda p: p.health_score or 999)
    priority_ranking = [p.name for p in projects]

    scores = [p.health_score for p in projects if p.health_score is not None]
    avg = sum(scores) / len(scores) if scores else None

    return EcosystemResponse(
        projects=projects,
        priority_ranking=priority_ranking,
        total_projects=len(projects),
        avg_health=round(avg, 1) if avg is not None else None,
    )


@router.get("/{owner}/{repo}/history")
async def get_project_history(owner: str, repo: str, limit: int = 30) -> Dict[str, Any]:
    """Health score history for a specific project (for trend charts)."""
    full_repo = f"{owner}/{repo}"
    scans = get_repo_scans(full_repo, limit=limit)

    return {
        "repo": full_repo,
        "history": [
            {
                "score": s["health_score"],
                "grade": s["grade"],
                "date": s["completed"],
            }
            for s in scans
        ],
        "total_scans": len(scans),
    }
