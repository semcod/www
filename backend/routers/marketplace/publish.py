"""Marketplace publish endpoints - install/uninstall apps."""

from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from routers.marketplace.models import InstallRequest, InstallResponse

router = APIRouter(tags=["marketplace"])


@router.post("/install", response_model=InstallResponse)
async def install_app(
    request: InstallRequest,
    user: dict = Depends(get_current_user),
) -> InstallResponse:
    """Install Semcod app on a repository.

    This:
    1. Creates/gets tenant
    2. Creates/gets repository
    3. Stores installation in DB
    4. Sets up webhook on the provider
    """
    from database import (
        get_or_create_tenant,
        get_or_create_repository,
        create_installation,
    )

    token = (
        user.get("github_token") or user.get("gitlab_token") or user.get("gitea_token")
    )
    if not token:
        raise HTTPException(401, "Git provider token required")

    # Get or create tenant
    provider_user_id = str(
        user.get("github_id")
        or user.get("gitlab_id")
        or user.get("gitea_id")
        or user.get("id")
    )
    tenant = get_or_create_tenant(
        provider=request.provider,
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
        name=user.get("name", ""),
        avatar_url=user.get("avatar_url", ""),
    )

    # Get or create repository
    repo_parts = request.repo.split("/")
    repo_name = repo_parts[-1] if len(repo_parts) > 1 else request.repo
    repo = get_or_create_repository(
        tenant_id=tenant["id"],
        provider=request.provider,
        repo_provider_id=str(user.get("id")),  # In production, fetch from provider API
        name=repo_name,
        full_name=request.repo,
    )

    # Create installation
    installation = create_installation(
        tenant_id=tenant["id"],
        repository_id=repo["id"],
        apps=request.apps,
    )

    # Setup webhook (async task in production)
    try:
        await _setup_webhook(request.repo, request.provider, token)
    except Exception as e:
        print(f"[install] Webhook setup failed: {e}")

    return InstallResponse(
        status="installed",
        repo=request.repo,
        provider=request.provider,
        apps=request.apps,
        webhook_url=f"/webhook/{request.provider}",
    )


@router.delete("/install")
async def uninstall_app(
    repo: str,
    provider: str,
    user: dict = Depends(get_current_user),
):
    """Remove Semcod app from a repository."""
    from database import (
        get_or_create_tenant,
        get_repository_by_full_name,
        delete_installation,
    )

    # Get tenant
    provider_user_id = str(
        user.get("github_id")
        or user.get("gitlab_id")
        or user.get("gitea_id")
        or user.get("id")
    )
    tenant = get_or_create_tenant(
        provider=provider,
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
    )

    # Get repository
    repo_data = get_repository_by_full_name(tenant["id"], provider, repo)
    if not repo_data:
        raise HTTPException(404, "Repository not found")

    # Delete installation (soft delete)
    delete_installation(tenant["id"], repo_data["id"])

    return {"status": "uninstalled", "repo": repo, "provider": provider}


@router.get("/installations")
async def list_installations(
    user: dict = Depends(get_current_user),
) -> List[Dict]:
    """List all installations for the current user."""
    from database import get_or_create_tenant, get_tenant_installations

    # Get tenant
    provider_user_id = str(
        user.get("github_id")
        or user.get("gitlab_id")
        or user.get("gitea_id")
        or user.get("id")
    )
    tenant = get_or_create_tenant(
        provider=user.get("provider", "github"),
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
    )

    installs = get_tenant_installations(tenant["id"])
    return [
        {
            "repo": inst["repo_full_name"],
            "provider": inst["repo_provider"],
            "apps": inst["apps"],
            "installed_at": inst["installed_at"],
            "last_scan": inst.get("last_scan_at"),
            "score": inst.get("last_scan_score"),
        }
        for inst in installs
    ]


@router.get("/apps/status")
async def get_app_status(
    repo: str,
    provider: str,
    user: dict = Depends(get_current_user),
):
    """Get installation status and last scan results for a repo."""
    from database import (
        get_or_create_tenant,
        get_repository_by_full_name,
        get_installation,
    )
    from routers.marketplace.models import AppStatusResponse

    # Get tenant
    provider_user_id = str(
        user.get("github_id")
        or user.get("gitlab_id")
        or user.get("gitea_id")
        or user.get("id")
    )
    tenant = get_or_create_tenant(
        provider=provider,
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
    )

    # Get repository
    repo_data = get_repository_by_full_name(tenant["id"], provider, repo)
    if not repo_data:
        return AppStatusResponse(
            repo=repo,
            provider=provider,
            installed=False,
            apps=[],
        )

    # Get installation
    install = get_installation(tenant["id"], repo_data["id"])

    if not install:
        return AppStatusResponse(
            repo=repo,
            provider=provider,
            installed=False,
            apps=[],
        )

    return AppStatusResponse(
        repo=repo,
        provider=provider,
        installed=True,
        apps=install.get("apps", []),
        last_scan=install.get("last_scan_at"),
        score=install.get("last_scan_score"),
    )


async def _setup_webhook(repo: str, provider: str, token: str):
    """Setup webhook on the git provider."""
    from adapters.github import GitHubAdapter
    from adapters.gitlab import GitLabAdapter
    from adapters.gitea import GiteaAdapter

    # Map provider to adapter
    adapter_map = {
        "github": GitHubAdapter,
        "gitlab": GitLabAdapter,
        "gitea": GiteaAdapter,
    }

    adapter_class = adapter_map.get(provider)
    if not adapter_class:
        raise ValueError(f"Unknown provider: {provider}")

    # Note: Actual webhook setup requires specific API calls
    # This is a placeholder - implement based on provider API
    print(f"[webhook] Setting up {provider} webhook for {repo}")

    # In production:
    # 1. Create webhook via provider API
    # 2. Verify webhook signature setup
    # 3. Store webhook ID for management
