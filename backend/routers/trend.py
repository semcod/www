"""Trend and scan-diff API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from services.scan_service import get_repo_scans

router = APIRouter()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_completed(iso: str) -> datetime:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _trend_direction(scores: List[int]) -> str:
    if len(scores) < 2:
        return "stable"
    delta = scores[-1] - scores[0]
    if delta > 3:
        return "improving"
    if delta < -3:
        return "degrading"
    return "stable"


def _filter_by_days(scans: List[Dict], days: int) -> List[Dict]:
    if days <= 0:
        return scans
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [s for s in scans if _parse_completed(s["completed"]) >= cutoff]


def _build_diff_proposals(prev: Dict, curr: Dict) -> List[Dict]:
    proposals = []
    prev_cc = prev["stats"].get("complexity", {}).get("cc_avg", 0)
    curr_cc = curr["stats"].get("complexity", {}).get("cc_avg", 0)
    if curr_cc > prev_cc + 0.5:
        proposals.append(
            {
                "type": "complexity_regression",
                "target": curr["repo"],
                "reason": f"Average CC increased from {prev_cc:.1f} to {curr_cc:.1f}",
                "effort": "medium",
                "impact": round((curr_cc - prev_cc) * 10),
                "auto_fixable": False,
                "llm_prompt": (
                    f"Identify functions with cyclomatic complexity above 10 in {curr['repo']} "
                    f"and propose refactoring to reduce average CC from {curr_cc:.1f} to below {prev_cc:.1f}."
                ),
            }
        )

    prev_dup = prev["stats"].get("duplication", {}).get("duplication_groups", 0)
    curr_dup = curr["stats"].get("duplication", {}).get("duplication_groups", 0)
    if curr_dup > prev_dup:
        proposals.append(
            {
                "type": "duplication_increase",
                "target": curr["repo"],
                "reason": f"Duplication groups increased from {prev_dup} to {curr_dup}",
                "effort": "low",
                "impact": (curr_dup - prev_dup) * 5,
                "auto_fixable": True,
                "llm_prompt": (
                    f"Find and eliminate {curr_dup - prev_dup} new duplication groups "
                    f"introduced in {curr['repo']} since the last scan."
                ),
            }
        )

    prev_q_errors = prev["stats"].get("quality", {}).get("errors", 0)
    curr_q_errors = curr["stats"].get("quality", {}).get("errors", 0)
    if curr_q_errors > prev_q_errors:
        proposals.append(
            {
                "type": "quality_regression",
                "target": curr["repo"],
                "reason": f"Quality errors increased from {prev_q_errors} to {curr_q_errors}",
                "effort": "low",
                "impact": (curr_q_errors - prev_q_errors) * 8,
                "auto_fixable": True,
                "llm_prompt": (
                    f"Fix {curr_q_errors - prev_q_errors} new quality errors in {curr['repo']} "
                    f"(ruff/mypy/bandit). List each violation with a one-line fix."
                ),
            }
        )

    proposals.sort(key=lambda p: p["impact"], reverse=True)
    return proposals


# ─── Trend endpoints ───────────────────────────────────────────────────────────


@router.get("/api/trend/{owner}/{repo}")
async def get_repo_trend(owner: str, repo: str, days: int = 30) -> Dict:
    """
    Get historical health scores for a repository.

    Returns time-series data suitable for a trend chart.
    """
    full_repo = f"{owner}/{repo}"
    scans = get_repo_scans(full_repo)
    if not scans:
        raise HTTPException(404, f"No scans found for {full_repo}")

    scans = _filter_by_days(scans, days)
    if not scans:
        raise HTTPException(404, f"No scans in the last {days} days for {full_repo}")

    scores = [s["health_score"] for s in scans]
    points = [
        {
            "date": s["completed"],
            "health_score": s["health_score"],
            "grade": s["grade"],
            "sandbox": s["sandbox"],
        }
        for s in scans
    ]

    return {
        "meta": {
            "generated_at": _utc_now_iso(),
            "repository": full_repo,
            "days": days,
            "scan_count": len(scans),
        },
        "trend": {
            "direction": _trend_direction(scores),
            "delta": scores[-1] - scores[0] if len(scores) >= 2 else 0,
            "best": max(scores),
            "worst": min(scores),
            "latest": scores[-1],
        },
        "points": points,
    }


@router.get("/api/trend/{owner}/{repo}/compare")
async def compare_repo_trend(owner: str, repo: str, days: int = 30) -> Dict:
    """
    Compare the latest scan against the scan from {days} ago.

    Returns a before/after summary with delta and regression flags.
    """
    full_repo = f"{owner}/{repo}"
    scans = get_repo_scans(full_repo)
    if len(scans) < 2:
        raise HTTPException(422, f"Need at least 2 scans for {full_repo} to compare")

    recent = _filter_by_days(scans, days)
    scan_after = scans[-1]
    baseline = [s for s in scans if s not in recent and s is not scan_after]

    scan_before = baseline[-1] if baseline else scans[0]

    score_delta = scan_after["health_score"] - scan_before["health_score"]
    cc_before = scan_before["stats"].get("complexity", {}).get("cc_avg", 0)
    cc_after = scan_after["stats"].get("complexity", {}).get("cc_avg", 0)

    return {
        "meta": {
            "generated_at": _utc_now_iso(),
            "repository": full_repo,
            "days": days,
        },
        "before": {
            "date": scan_before["completed"],
            "health_score": scan_before["health_score"],
            "grade": scan_before["grade"],
            "cc_avg": cc_before,
        },
        "after": {
            "date": scan_after["completed"],
            "health_score": scan_after["health_score"],
            "grade": scan_after["grade"],
            "cc_avg": cc_after,
        },
        "delta": {
            "health_score": score_delta,
            "cc_avg": round(cc_after - cc_before, 2),
            "regression": score_delta < -5,
        },
    }


# ─── Scan diff endpoint ────────────────────────────────────────────────────────


@router.get("/api/scan/diff/{owner}/{repo}")
async def get_scan_diff(owner: str, repo: str) -> Dict:
    """
    Compare the latest scan against the previous one for a repository.

    Returns delta metrics and ranked improvement proposals.
    Each auto-fixable proposal includes an llm_prompt for patch generation.
    """
    full_repo = f"{owner}/{repo}"
    scans = get_repo_scans(full_repo, limit=2)
    if len(scans) < 2:
        raise HTTPException(
            422,
            f"Need at least 2 scans for {full_repo}. Run another scan to see the diff.",
        )

    prev, curr = scans[-2], scans[-1]

    score_delta = curr["health_score"] - prev["health_score"]
    cc_prev = prev["stats"].get("complexity", {}).get("cc_avg", 0)
    cc_curr = curr["stats"].get("complexity", {}).get("cc_avg", 0)
    dup_prev = prev["stats"].get("duplication", {}).get("duplication_groups", 0)
    dup_curr = curr["stats"].get("duplication", {}).get("duplication_groups", 0)
    err_prev = prev["stats"].get("quality", {}).get("errors", 0)
    err_curr = curr["stats"].get("quality", {}).get("errors", 0)

    new_issues = max(0, dup_curr - dup_prev) + max(0, err_curr - err_prev)
    fixed_issues = max(0, dup_prev - dup_curr) + max(0, err_prev - err_curr)

    proposals = _build_diff_proposals(prev, curr)

    return {
        "meta": {
            "generated_at": _utc_now_iso(),
            "repository": full_repo,
        },
        "delta": {
            "score_change": score_delta,
            "new_issues": new_issues,
            "fixed_issues": fixed_issues,
            "regressions": [p["type"] for p in proposals],
            "cc_avg_change": round(cc_curr - cc_prev, 2),
        },
        "scans": {
            "previous": {
                "date": prev["completed"],
                "health_score": prev["health_score"],
                "grade": prev["grade"],
            },
            "current": {
                "date": curr["completed"],
                "health_score": curr["health_score"],
                "grade": curr["grade"],
            },
        },
        "proposals": proposals,
    }
