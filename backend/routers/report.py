"""Report page redirect."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from config import FRONTEND_URL

router = APIRouter()


@router.get("/report/{owner}/{repo}")
async def report_page(owner: str, repo: str):
    """Redirect to frontend report page."""
    return RedirectResponse(f"{FRONTEND_URL}/report/{owner}/{repo}")
