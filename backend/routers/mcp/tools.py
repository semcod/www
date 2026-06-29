import hashlib
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from .models import MCPTool, MCPToolRequest
from services.scan_service import get_recent_scans
from store import audit_results

router = APIRouter()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_audit_id(value: str, now_iso: str) -> str:
    return hashlib.sha256(f"{value}-{now_iso}".encode()).hexdigest()[:12]


def _required_argument(arguments: dict, name: str) -> str:
    value = arguments.get(name)
    if not value:
        raise HTTPException(400, f"{name} is required")
    return value


def _parse_public_repo(repo_url: str) -> tuple[str, str] | None:
    match = (
        re.search(r"github\.com/([^/]+)/([^/\.]+)", repo_url)
        or re.search(r"gitlab\.com/([^/]+)/([^/\.]+)", repo_url)
        or re.search(r"bitbucket\.org/([^/]+)/([^/\.]+)", repo_url)
    )
    if not match:
        return None
    return match.group(1), match.group(2)


def _normalize_repo(repo: str) -> str:
    if ":" in repo:
        _, repo = repo.split(":", 1)
    return repo


def _invoke_start_audit(arguments: dict) -> dict:
    repo = _required_argument(arguments, "repo")
    now_iso = _utc_now_iso()
    audit_id = _build_audit_id(repo, now_iso)
    audit_results[audit_id] = {
        "status": "running",
        "repo": repo,
        "started": now_iso,
    }
    return {
        "audit_id": audit_id,
        "status": "running",
        "message": f"Audit started for {repo}. Use get_scan_status to check progress.",
    }


def _invoke_get_status(arguments: dict) -> dict:
    audit_id = _required_argument(arguments, "audit_id")
    result = audit_results.get(audit_id)
    if not result:
        raise HTTPException(404, f"Audit not found: {audit_id}")
    return {
        "audit_id": audit_id,
        **result,
    }


def _invoke_get_metrics(arguments: dict) -> dict:
    repo = _normalize_repo(_required_argument(arguments, "repo"))
    scans = get_recent_scans(1000)
    repo_scans = [scan for scan in scans if scan["repo"] == repo]
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


def _invoke_analyze_public(arguments: dict) -> dict:
    repo_url = _required_argument(arguments, "repo_url")
    parsed_repo = _parse_public_repo(repo_url)
    if not parsed_repo:
        raise HTTPException(400, "Could not parse owner/repo from URL")

    owner, repo = parsed_repo
    repo_name = f"{owner}/{repo}"
    now_iso = _utc_now_iso()
    audit_id = _build_audit_id(repo_name, now_iso)
    audit_results[audit_id] = {
        "status": "running",
        "repo": repo_name,
        "sandbox": True,
        "repo_url": repo_url,
        "started": now_iso,
    }
    return {
        "audit_id": audit_id,
        "status": "running",
        "repo": repo_name,
        "message": f"Sandbox analysis started for {repo_name}. Use get_scan_status to check progress.",
    }


@router.get("")
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


@router.post("/invoke")
async def mcp_invoke_tool(request: MCPToolRequest) -> dict:
    """Invoke an MCP tool with the provided arguments."""
    handlers = {
        "start_audit": _invoke_start_audit,
        "get_scan_status": _invoke_get_status,
        "get_repository_metrics": _invoke_get_metrics,
        "analyze_public_repo": _invoke_analyze_public,
    }

    handler = handlers.get(request.name)
    if not handler:
        raise HTTPException(400, f"Unknown tool: {request.name}")

    return handler(request.arguments)
