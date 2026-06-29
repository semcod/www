from fastapi import APIRouter

from .resources import router as resources_router
from .tools import router as tools_router, mcp_invoke_tool
from .models import MCPToolRequest

router = APIRouter(prefix="/mcp", tags=["mcp"])

router.include_router(resources_router, prefix="/resources")
router.include_router(tools_router, prefix="/tools")

router.add_api_route("/invoke", mcp_invoke_tool, methods=["POST"])


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
