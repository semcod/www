"""
System routes - health checks and configuration
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import re

from config import PUBLIC_URL
from store import audit_results, badge_cache

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Health check endpoint with cache stats."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "tools": ["code2llm", "redup", "pyqual", "regix", "vallm"],
        "audits_cached": len(audit_results),
        "badges_cached": len(badge_cache),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/config/domain")
async def get_domain_config():
    """Return the configured domain from environment."""
    domain = re.sub(r"^https?://", "", PUBLIC_URL)
    domain = re.sub(r":[0-9]+$", "", domain)
    if domain == "localhost":
        domain = "semcod.com"
    return {"domain": domain}
