"""Standardized metrics API for remote retrieval."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from config import PUBLIC_URL
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path

from services.scan_service import get_recent_scans, get_total_scan_count

router = APIRouter()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/api/metrics/standard")
async def get_standard_metrics(limit: int = 10) -> Dict:
    """
    Get standardized metrics for recent scans.
    This endpoint provides a consistent format for remote clients.
    
    Response format:
    {
        "meta": {
            "generated_at": "ISO timestamp",
            "total_scans": 123,
            "returned_scans": 10
        },
        "scans": [
            {
                "repository": "owner/repo",
                "platform": "github|gitlab|bitbucket",
                "health_score": 85,
                "grade": "A",
                "metrics": {
                    "files": 150,
                    "lines_of_code": 25000,
                    "languages": {"Python": 18000, "JavaScript": 7000},
                    "complexity": {"avg_cyclomatic": 3.5, "functions": 500},
                    "duplication": {"groups": 5, "recoverable_lines": 200},
                    "quality": {"passed": 95, "warnings": 3, "errors": 2}
                },
                "scanned_at": "ISO timestamp",
                "badge_url": "https://semcod.com/badge/owner-repo.svg"
            }
        ]
    }
    """
    try:
        scans = get_recent_scans(limit)
        total = get_total_scan_count()
        
        formatted_scans = []
        for scan in scans:
            # Determine platform from repo URL pattern
            platform = "github"
            if "gitlab" in scan["repo"].lower():
                platform = "gitlab"
            elif "bitbucket" in scan["repo"].lower():
                platform = "bitbucket"
            
            formatted_scan = {
                "repository": scan["repo"],
                "platform": platform,
                "health_score": scan["health_score"],
                "grade": scan["grade"],
                "metrics": {
                    "files": scan["stats"].get("total_files", 0),
                    "lines_of_code": scan["stats"].get("total_lines", 0),
                    "languages": scan["stats"].get("languages", {}),
                    "complexity": {
                        "avg_cyclomatic": scan["stats"].get("complexity", {}).get("cc_avg", 0),
                        "functions": scan["stats"].get("complexity", {}).get("functions", 0),
                    },
                    "duplication": {
                        "groups": scan["stats"].get("duplication", {}).get("duplication_groups", 0),
                        "recoverable_lines": scan["stats"].get("duplication", {}).get("recoverable_lines", 0),
                    },
                    "quality": {
                        "passed": scan["stats"].get("quality", {}).get("passed", 0),
                        "warnings": scan["stats"].get("quality", {}).get("warnings", 0),
                        "errors": scan["stats"].get("quality", {}).get("errors", 0),
                    },
                },
                "scanned_at": scan["completed"],
                "badge_url": scan.get("badge_url", ""),
            }
            formatted_scans.append(formatted_scan)
        
        return {
            "meta": {
                "generated_at": _utc_now_iso(),
                "total_scans": total,
                "returned_scans": len(formatted_scans),
            },
            "scans": formatted_scans,
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve metrics: {str(e)}")


@router.get("/api/metrics/summary")
async def get_metrics_summary() -> Dict:
    """
    Get summary statistics of all scans.
    Useful for dashboards and monitoring.
    """
    try:
        scans = get_recent_scans(1000)
        
        if not scans:
            return {
                "meta": {
                    "generated_at": _utc_now_iso(),
                    "total_scans": 0,
                },
                "summary": {
                    "avg_health_score": 0,
                    "grade_distribution": {},
                    "total_files": 0,
                    "total_lines": 0,
                    "platform_distribution": {},
                },
            }
        
        total_health = sum(s["health_score"] for s in scans)
        avg_health = total_health / len(scans)
        
        grade_dist = {}
        for scan in scans:
            grade = scan["grade"]
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        total_files = sum(s["stats"].get("total_files", 0) for s in scans)
        total_lines = sum(s["stats"].get("total_lines", 0) for s in scans)
        
        platform_dist = {"github": 0, "gitlab": 0, "bitbucket": 0}
        for scan in scans:
            if "gitlab" in scan["repo"].lower():
                platform_dist["gitlab"] += 1
            elif "bitbucket" in scan["repo"].lower():
                platform_dist["bitbucket"] += 1
            else:
                platform_dist["github"] += 1
        
        return {
            "meta": {
                "generated_at": _utc_now_iso(),
                "total_scans": len(scans),
            },
            "summary": {
                "avg_health_score": round(avg_health, 2),
                "grade_distribution": grade_dist,
                "total_files": total_files,
                "total_lines": total_lines,
                "platform_distribution": platform_dist,
            },
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve summary: {str(e)}")


@router.get("/api/metrics/repository/{repo_path:path}")
async def get_repository_metrics(repo_path: str) -> Dict:
    """
    Get metrics for a specific repository.
    repo_path format: "owner/repo" or with platform prefix "github:owner/repo"
    """
    try:
        # Parse repo_path to extract repo name
        if ":" in repo_path:
            platform, repo = repo_path.split(":", 1)
        else:
            platform = "github"
            repo = repo_path
        
        # Get all scans and filter for this repo
        scans = get_recent_scans(1000)
        repo_scans = [s for s in scans if s["repo"] == repo]
        
        if not repo_scans:
            raise HTTPException(404, f"No scans found for repository: {repo}")
        
        # Return the most recent scan
        latest_scan = repo_scans[0]
        
        return {
            "meta": {
                "generated_at": _utc_now_iso(),
                "repository": repo,
                "platform": platform,
                "scan_count": len(repo_scans),
            },
            "scan": {
                "health_score": latest_scan["health_score"],
                "grade": latest_scan["grade"],
                "metrics": {
                    "files": latest_scan["stats"].get("total_files", 0),
                    "lines_of_code": latest_scan["stats"].get("total_lines", 0),
                    "languages": latest_scan["stats"].get("languages", {}),
                },
                "scanned_at": latest_scan["completed"],
                "badge_url": latest_scan.get("badge_url", ""),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve repository metrics: {str(e)}")


@router.get("/api/metrics/prompt")
async def download_project_prompt():
    """Download the project prompt.txt file for LLM analysis."""
    prompt_path = Path(__file__).parent.parent.parent / "project" / "prompt.txt"
    
    if not prompt_path.exists():
        raise HTTPException(404, "Project prompt file not found")
    
    return FileResponse(
        prompt_path,
        media_type="text/plain",
        filename="semcod-project-prompt.txt"
    )


@router.get("/api/metrics/prompt/markdown")
async def download_project_prompt_markdown():
    """Download the project prompt as markdown format."""
    prompt_path = Path(__file__).parent.parent.parent / "project" / "prompt.txt"
    
    if not prompt_path.exists():
        raise HTTPException(404, "Project prompt file not found")
    
    with open(prompt_path, 'r') as f:
        content = f.read()
    
    # Convert to markdown format
    markdown_content = f"""# Semcod Project Analysis Prompt

```text
{content}
```

*Generated by Semcod - Code Health Analysis Tool*
"""
    
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": "attachment; filename=semcod-project-prompt.md"
        }
    )
