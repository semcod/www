"""Marketplace API router - mounts all marketplace sub-routers."""

from fastapi import APIRouter

from .browse import router as browse_router
from .publish import router as publish_router
from .deploy import router as deploy_router
from .billing import router as billing_router
from .connect import router as connect_router
from .quality import router as quality_router
from .models import (
    PreviewRequest,
    PreviewResponse,
    InstallRequest,
    InstallResponse,
    AppStatusResponse,
    AutoFixRequest,
    AutoFixResponse,
)

# Mount all sub-routers
router = APIRouter(prefix="/api", tags=["marketplace"])
router.include_router(browse_router)
router.include_router(publish_router)
router.include_router(deploy_router)
router.include_router(billing_router)
router.include_router(connect_router)
router.include_router(quality_router)

# Re-export models for backward compatibility
__all__ = [
    "router",
    "PreviewRequest",
    "PreviewResponse",
    "InstallRequest",
    "InstallResponse",
    "AppStatusResponse",
    "AutoFixRequest",
    "AutoFixResponse",
]
