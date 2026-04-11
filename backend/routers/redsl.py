"""ReDSL integration router — analyze, health, refactor, auto-pr, badge."""

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from services.redsl_client import RedslClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/redsl", tags=["redsl"])

redsl = RedslClient()


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    project_path: str = Field(..., description="Absolute path to the project directory")
    project_toon: Optional[str] = Field(None, description="Optional project_toon YAML content")


class RefactorRequest(BaseModel):
    project_path: str = Field(..., description="Absolute path to the project directory")
    max_actions: int = Field(10, ge=1, le=50, description="Max refactoring actions")
    dry_run: bool = Field(True, description="Preview only, no changes")


class AutoPrRequest(BaseModel):
    repo: str = Field(..., description="GitHub repo (owner/repo)")
    project_path: str = Field(..., description="Absolute path to the project directory")
    max_actions: int = Field(5, ge=1, le=20)
    branch_prefix: str = "semcod-redsl"


# ─── Engine status ────────────────────────────────────────────────────────────

@router.get("/status")
async def get_status():
    """Check if reDSL engine is available."""
    available = await redsl.health()
    return {"available": available, "url": redsl.base_url}


# ─── Analyze ──────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze(body: AnalyzeRequest, bg: BackgroundTasks):
    """Run reDSL analysis on a project."""
    available = await redsl.health()
    if not available:
        raise HTTPException(503, "reDSL engine is not available. Start it with: docker-compose up agent")
    try:
        result = await redsl.analyze(body.project_path, body.project_toon)
        return {"status": "analyzed", "result": result}
    except Exception as exc:
        logger.error("reDSL analyze failed: %s", exc)
        raise HTTPException(500, f"Analysis failed: {exc}")


# ─── Health Score ─────────────────────────────────────────────────────────────

@router.post("/health")
async def get_health(body: AnalyzeRequest):
    """Get unified health score for a project."""
    available = await redsl.health()
    if not available:
        raise HTTPException(503, "reDSL engine is not available")
    try:
        result = await redsl.health_score(body.project_path)
        return result
    except Exception as exc:
        logger.error("reDSL health check failed: %s", exc)
        raise HTTPException(500, f"Health check failed: {exc}")


# ─── Refactor ─────────────────────────────────────────────────────────────────

@router.post("/refactor")
async def run_refactor(body: RefactorRequest, bg: BackgroundTasks):
    """Run reDSL refactoring on a project."""
    available = await redsl.health()
    if not available:
        raise HTTPException(503, "reDSL engine is not available")
    try:
        result = await redsl.refactor(
            project_path=body.project_path,
            max_actions=body.max_actions,
            dry_run=body.dry_run,
            fmt="json",
        )
        return {"status": "refactored" if not body.dry_run else "preview", "result": result}
    except Exception as exc:
        logger.error("reDSL refactor failed: %s", exc)
        raise HTTPException(500, f"Refactor failed: {exc}")


# ─── Decide (dry-run decisions) ───────────────────────────────────────────────

@router.post("/decide")
async def run_decide(body: AnalyzeRequest):
    """Evaluate DSL rules without execution — returns decisions only."""
    available = await redsl.health()
    if not available:
        raise HTTPException(503, "reDSL engine is not available")
    try:
        decisions = await redsl.decide(body.project_path)
        return {"decisions": decisions}
    except Exception as exc:
        logger.error("reDSL decide failed: %s", exc)
        raise HTTPException(500, f"Decide failed: {exc}")


# ─── Batch Hybrid ────────────────────────────────────────────────────────────

@router.post("/batch-hybrid")
async def run_batch_hybrid(project_path: str, max_changes: int = 30):
    """Run hybrid quality refactoring (no LLM needed)."""
    available = await redsl.health()
    if not available:
        raise HTTPException(503, "reDSL engine is not available")
    try:
        result = await redsl.batch_hybrid(project_path, max_changes)
        return {"status": "completed", "result": result}
    except Exception as exc:
        logger.error("reDSL batch-hybrid failed: %s", exc)
        raise HTTPException(500, f"Batch hybrid failed: {exc}")


# ─── Health Badge (SVG) ──────────────────────────────────────────────────────

_GRADE_COLORS = {
    "A+": "brightgreen", "A": "green",
    "B+": "yellowgreen", "B": "yellow",
    "C": "orange", "D": "red", "F": "red",
}


@router.get("/badge/{owner}/{repo}")
async def health_badge(owner: str, repo: str):
    """SVG badge with health score — for README.md embedding."""
    full_repo = f"{owner}/{repo}"

    # Try to get cached health from scans DB
    try:
        from services.scan_service import get_repo_scans
        scans = get_repo_scans(full_repo, limit=1)
        if scans:
            score = scans[-1].get("health_score", 0)
            grade = _score_to_grade(score)
        else:
            grade = "?"
            score = None
    except Exception:
        grade = "?"
        score = None

    color = _GRADE_COLORS.get(grade, "lightgrey")
    label_text = "code health"
    value_text = f"{grade}" if score is None else f"{grade} ({score})"

    svg = _make_badge_svg(label_text, value_text, color)
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-cache"})


def _score_to_grade(score: int) -> str:
    if score >= 95:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 75:
        return "B+"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def _make_badge_svg(label: str, value: str, color: str) -> str:
    """Generate a shields.io-style SVG badge."""
    lw = len(label) * 7 + 10
    vw = len(value) * 7 + 10
    tw = lw + vw
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="m"><rect width="{tw}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{vw}" height="20" fill="{color}"/>
    <rect width="{tw}" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{lw // 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{lw // 2}" y="14">{label}</text>
    <text x="{lw + vw // 2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{lw + vw // 2}" y="14">{value}</text>
  </g>
</svg>'''
