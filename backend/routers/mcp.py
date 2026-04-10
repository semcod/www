"""MCP (Model Context Protocol) router for AI assistant integration.

This router implements the Model Context Protocol allowing AI assistants
(Claude, Cascade, etc.) to interact with Semcod programmatically.

Resources:
    - scans://list - List recent scans
    - scan://{id} - Get specific scan details
    - metrics://summary - Get aggregated metrics

Tools:
    - start_audit - Start a new audit for a repository
    - get_scan_status - Check status of a running scan
    - get_repository_metrics - Get metrics for specific repository
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from store import audit_results, badge_cache, scan_history
from database import get_recent_scans, get_total_scan_count
from services.scoring import calculate_health_score, score_to_grade, generate_recommendations


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

router = APIRouter(prefix="/mcp", tags=["mcp"])


# ─── MCP Protocol Models ─────────────────────────────────────────────────────

class MCPResource(BaseModel):
    """MCP Resource definition."""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class MCPTool(BaseModel):
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: dict


class MCPResourceResponse(BaseModel):
    """MCP resource content response."""
    uri: str
    mime_type: str
    content: dict


# ─── Resources Discovery ─────────────────────────────────────────────────────

@router.get("/resources")
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


# ─── Resource Content ───────────────────────────────────────────────────────

@router.get("/resources/content")
async def mcp_get_resource(uri: str) -> MCPResourceResponse:
    """Get content of a specific MCP resource by URI."""
    
    if uri == "scans://list":
        scans = get_recent_scans(50)
        return MCPResourceResponse(
            uri=uri,
            mime_type="application/json",
            content={
                "scans": [
                    {
                        "audit_id": scan.get("audit_id", ""),
                        "repository": scan["repo"],
                        "health_score": scan["health_score"],
                        "grade": scan["grade"],
                        "status": scan.get("status", "complete"),
                        "scanned_at": scan["completed"],
                        "badge_url": scan.get("badge_url", ""),
                    }
                    for scan in scans
                ],
                "total_available": get_total_scan_count(),
            },
        )
    
    elif uri.startswith("scan://"):
        audit_id = uri.replace("scan://", "")
        scan = audit_results.get(audit_id)
        
        if not scan:
            # Try to find in scan history
            for s in scan_history:
                if s.get("audit_id") == audit_id:
                    scan = s
                    break
        
        if not scan:
            raise HTTPException(404, f"Scan not found: {audit_id}")
        
        return MCPResourceResponse(
            uri=uri,
            mime_type="application/json",
            content=scan,
        )
    
    elif uri == "metrics://summary":
        scans = get_recent_scans(1000)
        
        if not scans:
            summary = {
                "avg_health_score": 0,
                "grade_distribution": {},
                "total_files": 0,
                "total_lines": 0,
                "platform_distribution": {"github": 0, "gitlab": 0, "bitbucket": 0},
            }
        else:
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
            
            summary = {
                "avg_health_score": round(avg_health, 2),
                "grade_distribution": grade_dist,
                "total_files": total_files,
                "total_lines": total_lines,
                "platform_distribution": platform_dist,
            }
        
        return MCPResourceResponse(
            uri=uri,
            mime_type="application/json",
            content={
                "meta": {
                    "generated_at": _utc_now_iso(),
                    "total_scans": len(scans),
                },
                "summary": summary,
            },
        )
    
    elif uri.startswith("badge://"):
        repo_slug = uri.replace("badge://", "")
        repo = repo_slug.replace("-", "/", 1)
        cached = badge_cache.get(repo)
        
        return MCPResourceResponse(
            uri=uri,
            mime_type="application/json",
            content={
                "repository": repo,
                "cached": cached is not None,
                "score": cached["score"] if cached else None,
                "grade": cached["grade"] if cached else None,
                "weekly_issues": cached.get("weekly_issues") if cached else None,
                "updated": cached.get("updated") if cached else None,
            },
        )
    
    raise HTTPException(404, f"Unknown resource URI: {uri}")


# ─── Tools Discovery ─────────────────────────────────────────────────────────

@router.get("/tools")
async def mcp_list_tools() -> list[MCPTool]:
    """List all available MCP tools."""
    return [
        MCPTool(
            name="start_audit",
            description="Start a new code health audit for a repository",
            input_schema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'",
                    },
                    "token": {
                        "type": "string",
                        "description": "GitHub access token (optional for public repos in sandbox mode)",
                    },
                    "sandbox": {
                        "type": "boolean",
                        "description": "Use sandbox mode for public repos (no token needed)",
                        "default": False,
                    },
                },
                "required": ["repo"],
            },
        ),
        MCPTool(
            name="get_scan_status",
            description="Get the current status of a scan by its audit ID",
            input_schema={
                "type": "object",
                "properties": {
                    "audit_id": {
                        "type": "string",
                        "description": "The audit ID returned from start_audit",
                    },
                },
                "required": ["audit_id"],
            },
        ),
        MCPTool(
            name="get_repository_metrics",
            description="Get detailed metrics for a specific repository",
            input_schema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name' or platform prefix 'github:owner/name'",
                    },
                },
                "required": ["repo"],
            },
        ),
        MCPTool(
            name="analyze_public_repo",
            description="Analyze any public repository without authentication (sandbox mode)",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "Full repository URL (https://github.com/owner/repo)",
                    },
                },
                "required": ["repo_url"],
            },
        ),
    ]


# ─── Tool Invocation ─────────────────────────────────────────────────────────

class MCPToolRequest(BaseModel):
    """MCP tool invocation request."""
    name: str
    arguments: dict = Field(default_factory=dict)


@router.post("/invoke")
async def mcp_invoke_tool(request: MCPToolRequest) -> dict:
    """Invoke an MCP tool with the provided arguments."""
    
    if request.name == "start_audit":
        repo = request.arguments.get("repo")
        token = request.arguments.get("token", "sandbox")
        sandbox = request.arguments.get("sandbox", False)
        
        if not repo:
            raise HTTPException(400, "repo is required")
        
        # Generate audit ID
        audit_id = hashlib.sha256(
            f"{repo}-{_utc_now_iso()}".encode()
        ).hexdigest()[:12]

        # Store initial status
        audit_results[audit_id] = {
            "status": "running",
            "repo": repo,
            "started": _utc_now_iso(),
        }
        
        return {
            "audit_id": audit_id,
            "status": "running",
            "message": f"Audit started for {repo}. Use get_scan_status to check progress.",
        }
    
    elif request.name == "get_scan_status":
        audit_id = request.arguments.get("audit_id")
        
        if not audit_id:
            raise HTTPException(400, "audit_id is required")
        
        result = audit_results.get(audit_id)
        
        if not result:
            raise HTTPException(404, f"Audit not found: {audit_id}")
        
        return {
            "audit_id": audit_id,
            **result,
        }
    
    elif request.name == "get_repository_metrics":
        repo = request.arguments.get("repo")
        
        if not repo:
            raise HTTPException(400, "repo is required")
        
        # Remove platform prefix if present
        if ":" in repo:
            _, repo = repo.split(":", 1)
        
        # Find scans for this repo
        scans = get_recent_scans(1000)
        repo_scans = [s for s in scans if s["repo"] == repo]
        
        if not repo_scans:
            raise HTTPException(404, f"No scans found for repository: {repo}")
        
        latest = repo_scans[0]
        
        return {
            "repository": repo,
            "scan_count": len(repo_scans),
            "latest_scan": {
                "health_score": latest["health_score"],
                "grade": latest["grade"],
                "scanned_at": latest["completed"],
                "metrics": {
                    "files": latest["stats"].get("total_files", 0),
                    "lines_of_code": latest["stats"].get("total_lines", 0),
                    "languages": latest["stats"].get("languages", {}),
                },
            },
        }
    
    elif request.name == "analyze_public_repo":
        repo_url = request.arguments.get("repo_url")
        
        if not repo_url:
            raise HTTPException(400, "repo_url is required")
        
        # Parse owner/repo from URL
        match = (
            re.search(r"github\.com/([^/]+)/([^/\.]+)", repo_url)
            or re.search(r"gitlab\.com/([^/]+)/([^/\.]+)", repo_url)
            or re.search(r"bitbucket\.org/([^/]+)/([^/\.]+)", repo_url)
        )
        
        if not match:
            raise HTTPException(400, "Could not parse owner/repo from URL")
        
        owner, repo = match.group(1), match.group(2)
        audit_id = hashlib.sha256(
            f"{owner}/{repo}-{_utc_now_iso()}".encode()
        ).hexdigest()[:12]

        audit_results[audit_id] = {
            "status": "running",
            "repo": f"{owner}/{repo}",
            "sandbox": True,
            "repo_url": repo_url,
            "started": _utc_now_iso(),
        }
        
        return {
            "audit_id": audit_id,
            "status": "running",
            "repo": f"{owner}/{repo}",
            "message": f"Sandbox analysis started for {owner}/{repo}. Use get_scan_status to check progress.",
        }
    
    raise HTTPException(400, f"Unknown tool: {request.name}")


# ─── MCP Server Info ─────────────────────────────────────────────────────────

@router.get("/info")
async def mcp_server_info() -> dict:
    """Get MCP server information."""
    return {
        "name": "semcod-mcp",
        "version": "1.0.0",
        "protocol_version": "2024-11-05",
        "description": "Semcod Code Health Analysis - MCP Server",
        "resources": {
            "scans://list": "List recent code health scans",
            "scan://{audit_id}": "Get specific scan details",
            "metrics://summary": "Aggregated metrics summary",
            "badge://{repo_slug}": "Badge status for repository",
        },
        "tools": {
            "start_audit": "Start a new audit for a repository",
            "get_scan_status": "Check status of a running scan",
            "get_repository_metrics": "Get metrics for specific repository",
            "analyze_public_repo": "Analyze public repository in sandbox mode",
        },
    }
