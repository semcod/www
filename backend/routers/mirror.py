"""Mirror API - manage repo mirrors to local Gitea."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from routers.auth import get_current_user
from services.mirror import MirrorService, MirrorConfig, MirrorStatus

router = APIRouter(prefix="/api/mirror", tags=["mirror"])


# ─── Models ───────────────────────────────────────────────────────────────────


class CreateMirrorRequest(BaseModel):
    source_repo: str  # owner/repo
    source_provider: str  # github, gitlab
    target_repo: str  # owner/repo in Gitea
    gitea_url: str = "http://localhost:3000"
    sync_interval: int = 3600
    auto_deploy: bool = False
    deploy_branch: str = "main"
    docker_image: Optional[str] = None


class SyncMirrorRequest(BaseModel):
    mirror_id: str


class MirrorResponse(BaseModel):
    mirror_id: str
    status: str
    last_sync: Optional[str] = None
    last_commit: Optional[str] = None
    error: Optional[str] = None
    commits_synced: int = 0


class MirrorInfo(BaseModel):
    mirror_id: str
    source_repo: str
    source_provider: str
    target_repo: str
    gitea_url: str
    auto_deploy: bool
    created_at: str
    last_sync: Optional[str] = None
    status: str


# ─── In-memory storage (replace with database in production) ────────────────

_mirrors: Dict[str, Dict[str, Any]] = {}


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.post("/create", response_model=MirrorResponse)
async def create_mirror(
    request: CreateMirrorRequest,
    user: dict = Depends(get_current_user),
) -> MirrorResponse:
    """Create new mirror from GitHub/GitLab to local Gitea."""
    # Get tokens from user
    github_token = user.get("github_token")
    gitlab_token = user.get("gitlab_token")
    gitea_token = user.get("gitea_token") or "gitea"  # Default for local Gitea

    # Create mirror config
    config = MirrorConfig(
        source_repo=request.source_repo,
        source_provider=request.source_provider,
        target_repo=request.target_repo,
        gitea_url=request.gitea_url,
        sync_interval=request.sync_interval,
        auto_deploy=request.auto_deploy,
        deploy_branch=request.deploy_branch,
        docker_image=request.docker_image,
    )

    # Create mirror service
    service = MirrorService(
        github_token=github_token,
        gitlab_token=gitlab_token,
        gitea_token=gitea_token,
        gitea_url=request.gitea_url,
    )

    # Execute mirror
    result = await service.create_mirror(config, user.get("id"))

    # Store mirror info
    mirror_id = f"{request.source_provider}_{request.source_repo.replace('/', '_')}"
    _mirrors[mirror_id] = {
        "source_repo": request.source_repo,
        "source_provider": request.source_provider,
        "target_repo": request.target_repo,
        "gitea_url": request.gitea_url,
        "sync_interval": request.sync_interval,
        "auto_deploy": request.auto_deploy,
        "deploy_branch": request.deploy_branch,
        "docker_image": request.docker_image,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user.get("id"),
        "last_sync": result.last_sync,
        "status": result.status,
    }

    return MirrorResponse(
        mirror_id=result.mirror_id,
        status=result.status,
        last_sync=result.last_sync,
        last_commit=result.last_commit,
        error=result.error,
        commits_synced=result.commits_synced,
    )


@router.post("/sync", response_model=MirrorResponse)
async def sync_mirror(
    request: SyncMirrorRequest,
    user: dict = Depends(get_current_user),
) -> MirrorResponse:
    """Sync existing mirror with latest changes from source."""
    mirror_info = _mirrors.get(request.mirror_id)
    if not mirror_info:
        raise HTTPException(404, f"Mirror {request.mirror_id} not found")

    # Get tokens
    github_token = user.get("github_token")
    gitlab_token = user.get("gitlab_token")
    gitea_token = user.get("gitea_token") or "gitea"

    # Create config from stored mirror info
    config = MirrorConfig(
        source_repo=mirror_info["source_repo"],
        source_provider=mirror_info["source_provider"],
        target_repo=mirror_info["target_repo"],
        gitea_url=mirror_info["gitea_url"],
        sync_interval=mirror_info["sync_interval"],
        auto_deploy=mirror_info["auto_deploy"],
        deploy_branch=mirror_info["deploy_branch"],
        docker_image=mirror_info["docker_image"],
    )

    # Create mirror service
    service = MirrorService(
        github_token=github_token,
        gitlab_token=gitlab_token,
        gitea_token=gitea_token,
        gitea_url=mirror_info["gitea_url"],
    )

    # Execute sync
    result = await service.sync_mirror(config)

    # Update mirror info
    mirror_info["last_sync"] = result.last_sync
    mirror_info["status"] = result.status

    return MirrorResponse(
        mirror_id=result.mirror_id,
        status=result.status,
        last_sync=result.last_sync,
        last_commit=result.last_commit,
        error=result.error,
        commits_synced=result.commits_synced,
    )


@router.get("/list", response_model=List[MirrorInfo])
async def list_mirrors(user: dict = Depends(get_current_user)) -> List[MirrorInfo]:
    """List all mirrors for current user."""
    user_mirrors = [
        MirrorInfo(
            mirror_id=mirror_id,
            source_repo=info["source_repo"],
            source_provider=info["source_provider"],
            target_repo=info["target_repo"],
            gitea_url=info["gitea_url"],
            auto_deploy=info["auto_deploy"],
            created_at=info["created_at"],
            last_sync=info.get("last_sync"),
            status=info["status"],
        )
        for mirror_id, info in _mirrors.items()
        if info["user_id"] == user.get("id")
    ]
    return user_mirrors


@router.get("/{mirror_id}", response_model=MirrorInfo)
async def get_mirror(
    mirror_id: str,
    user: dict = Depends(get_current_user),
) -> MirrorInfo:
    """Get mirror by ID."""
    mirror_info = _mirrors.get(mirror_id)
    if not mirror_info:
        raise HTTPException(404, f"Mirror {mirror_id} not found")

    if mirror_info["user_id"] != user.get("id"):
        raise HTTPException(403, "Not authorized to access this mirror")

    return MirrorInfo(
        mirror_id=mirror_id,
        source_repo=mirror_info["source_repo"],
        source_provider=mirror_info["source_provider"],
        target_repo=mirror_info["target_repo"],
        gitea_url=mirror_info["gitea_url"],
        auto_deploy=mirror_info["auto_deploy"],
        created_at=mirror_info["created_at"],
        last_sync=mirror_info.get("last_sync"),
        status=mirror_info["status"],
    )


@router.delete("/{mirror_id}")
async def delete_mirror(
    mirror_id: str,
    user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """Delete mirror."""
    mirror_info = _mirrors.get(mirror_id)
    if not mirror_info:
        raise HTTPException(404, f"Mirror {mirror_id} not found")

    if mirror_info["user_id"] != user.get("id"):
        raise HTTPException(403, "Not authorized to delete this mirror")

    del _mirrors[mirror_id]

    return {"message": f"Mirror {mirror_id} deleted"}
