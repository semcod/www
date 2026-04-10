from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from .models import MCPResource, MCPResourceResponse
from database import get_recent_scans, get_total_scan_count
from store import audit_results, badge_cache, scan_history

router = APIRouter()

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _summarize_scan(scan: dict) -> dict:
    return {
        "audit_id": scan.get("audit_id", ""),
        "repository": scan["repo"],
        "health_score": scan["health_score"],
        "grade": scan["grade"],
        "status": scan.get("status", "complete"),
        "scanned_at": scan["completed"],
        "badge_url": scan.get("badge_url", ""),
    }

def _build_metrics_summary(scans: list[dict]) -> dict:
    if not scans:
        return {
            "avg_health_score": 0,
            "grade_distribution": {},
            "total_files": 0,
            "total_lines": 0,
            "platform_distribution": {"github": 0, "gitlab": 0, "bitbucket": 0},
        }

    total_health = sum(scan["health_score"] for scan in scans)
    grade_distribution = {}
    for scan in scans:
        grade = scan["grade"]
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

    platform_distribution = {"github": 0, "gitlab": 0, "bitbucket": 0}
    for scan in scans:
        repo_name = scan["repo"].lower()
        if "gitlab" in repo_name:
            platform_distribution["gitlab"] += 1
        elif "bitbucket" in repo_name:
            platform_distribution["bitbucket"] += 1
        else:
            platform_distribution["github"] += 1

    return {
        "avg_health_score": round(total_health / len(scans), 2),
        "grade_distribution": grade_distribution,
        "total_files": sum(scan["stats"].get("total_files", 0) for scan in scans),
        "total_lines": sum(scan["stats"].get("total_lines", 0) for scan in scans),
        "platform_distribution": platform_distribution,
    }

def _get_scans_list() -> tuple[str, dict]:
    scans = get_recent_scans(50)
    return "application/json", {
        "scans": [_summarize_scan(scan) for scan in scans],
        "total_available": get_total_scan_count(),
    }

def _get_scan_detail(audit_id: str) -> tuple[str, dict]:
    scan = audit_results.get(audit_id)
    if not scan:
        for history_scan in scan_history:
            if history_scan.get("audit_id") == audit_id:
                scan = history_scan
                break
    if not scan:
        raise HTTPException(404, f"Scan not found: {audit_id}")
    return "application/json", scan

def _get_metrics_summary() -> tuple[str, dict]:
    scans = get_recent_scans(1000)
    return "application/json", {
        "meta": {
            "generated_at": _utc_now_iso(),
            "total_scans": len(scans),
        },
        "summary": _build_metrics_summary(scans),
    }

def _get_badge_status(repo_slug: str) -> tuple[str, dict]:
    repo = repo_slug.replace("-", "/", 1)
    cached = badge_cache.get(repo)
    return "application/json", {
        "repository": repo,
        "cached": cached is not None,
        "score": cached["score"] if cached else None,
        "grade": cached["grade"] if cached else None,
        "weekly_issues": cached.get("weekly_issues") if cached else None,
        "updated": cached.get("updated") if cached else None,
    }


@router.get("")
async def mcp_list_resources() -> list[MCPResource]:
    """List all available MCP resources."""
    return [
        MCPResource(
            uri="scans://list",
            name="Recent Scans",
            description="List of recent code health scans with summaries",
            mime_type="application/json",
        ),
        MCPResource(
            uri="scan://{audit_id}",
            name="Scan Details",
            description="Full details of a specific scan including metrics and recommendations",
            mime_type="application/json",
        ),
        MCPResource(
            uri="metrics://summary",
            name="Metrics Summary",
            description="Aggregated metrics across all scans (avg health, grade distribution)",
            mime_type="application/json",
        ),
        MCPResource(
            uri="badge://{repo_slug}",
            name="Badge Status",
            description="Cached badge status for a repository (score, grade, issues)",
            mime_type="application/json",
        ),
    ]

@router.get("/content")
async def mcp_get_resource(uri: str) -> MCPResourceResponse:
    """Get content of a specific MCP resource by URI."""
    if uri == "scans://list":
        mime_type, content = _get_scans_list()
    elif uri.startswith("scan://"):
        audit_id = uri.replace("scan://", "")
        mime_type, content = _get_scan_detail(audit_id)
    elif uri == "metrics://summary":
        mime_type, content = _get_metrics_summary()
    elif uri.startswith("badge://"):
        repo_slug = uri.replace("badge://", "")
        mime_type, content = _get_badge_status(repo_slug)
    else:
        raise HTTPException(404, f"Unknown resource URI: {uri}")

    return MCPResourceResponse(
        uri=uri,
        mime_type=mime_type,
        content=content,
    )
