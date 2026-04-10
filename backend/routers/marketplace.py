"""Marketplace API - app installation, preview, and management."""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from adapters import get_adapter_for_event
from adapters.base import GitProvider
from apps.registry import get_registry
from apps.base import AppContext
from events.models import Event, EventType, ProviderType
from routers.auth import get_current_user
from database import (
    get_or_create_tenant,
    get_or_create_repository,
    get_repository_by_full_name,
    create_installation,
    get_installation,
    get_tenant_installations,
    delete_installation,
    update_installation_scan,
)

router = APIRouter(prefix="/api", tags=["marketplace"])


# ─── Models ───────────────────────────────────────────────────────────────────


class PreviewRequest(BaseModel):
    repo: str
    provider: str = "github"


class PreviewResponse(BaseModel):
    score: int
    comment: str
    issues: List[Dict]
    suggested_patch: Optional[str] = None


class InstallRequest(BaseModel):
    repo: str
    provider: str
    apps: List[str]


class InstallResponse(BaseModel):
    status: str
    repo: str
    provider: str
    apps: List[str]
    webhook_url: Optional[str] = None


class AppStatusResponse(BaseModel):
    repo: str
    provider: str
    installed: bool
    apps: List[str]
    last_scan: Optional[str] = None
    score: Optional[int] = None


# ─── Preview Endpoint ─────────────────────────────────────────────────────────


@router.post("/preview", response_model=PreviewResponse)
async def preview_pr_comment(
    request: PreviewRequest,
    user: dict = Depends(get_current_user),
) -> PreviewResponse:
    """Generate preview of PR comment for a repository.

    This endpoint simulates analysis on a sample diff to show
    users what the bot would comment before they install.
    """
    # Sample diff for preview (in production, fetch from repo's last PR)
    sample_diff = """
    - function calculateTotal(items) {
    -   let total = 0;
    -   for (let i = 0; i < items.length; i++) {
    -     total += items[i].price;
    -   }
    -   return total;
    - }
    + function calculateTotal(items) {
    +   return items.reduce((sum, item) => sum + item.price, 0);
    + }
    """

    # Run preview analysis through apps registry
    registry = get_registry()

    # Create mock event
    event = Event(
        type=EventType.PULL_REQUEST,
        provider=ProviderType(request.provider),
        repo=request.repo,
        action="opened",
        raw_payload={},
    )

    # Build context
    context = AppContext(
        repo=request.repo,
        event_type="pull_request",
        provider=request.provider,
        diff=sample_diff,
    )

    # Run apps and collect results
    results = registry.process_event(event)

    # Aggregate scores
    scores = []
    all_issues = []

    for app_name, result in results.items():
        if result.score is not None:
            scores.append(result.score)
        all_issues.extend(result.issues)

    avg_score = int(sum(scores) / len(scores)) if scores else 75

    # Format comment
    comment = _format_preview_comment(request.repo, avg_score, all_issues)

    return PreviewResponse(
        score=avg_score,
        comment=comment,
        issues=all_issues[:5],  # Limit to 5 issues
        suggested_patch=None,  # Could add auto-fix generation here
    )


# ─── Install Endpoints ──────────────────────────────────────────────────────────


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
    token = user.get("github_token") or user.get("gitlab_token") or user.get("gitea_token")
    if not token:
        raise HTTPException(401, "Git provider token required")

    # Get or create tenant
    provider_user_id = str(user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id"))
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
    # Get tenant
    provider_user_id = str(user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id"))
    from database import get_or_create_tenant
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
    # Get tenant
    provider_user_id = str(user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id"))
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
) -> AppStatusResponse:
    """Get installation status and last scan results for a repo."""
    # Get tenant
    provider_user_id = str(user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id"))
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


@router.get("/apps")
async def list_apps() -> List[Dict]:
    """List all available marketplace apps."""
    registry = get_registry()
    return registry.list_apps()


# ─── Helper Functions ───────────────────────────────────────────────────────────


def _format_preview_comment(repo: str, score: int, issues: List[Dict]) -> str:
    """Format preview comment like GitHub PR comment."""
    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"

    comment = f"""## {emoji} Semcod Preview Analysis

**Repository:** `{repo}`
**Health Score:** {score}/100 (Grade {grade})

"""

    if issues:
        comment += "### Issues Found\n"
        for issue in issues[:5]:
            icon = "🔴" if issue.get("severity") == "high" else "🟡"
            comment += f"- {icon} **{issue.get('type', 'issue')}**: {issue.get('message', '')}\n"
        comment += "\n"
    else:
        comment += "✅ No major issues detected!\n\n"

    comment += """### Next Steps
- Install Semcod to enable automatic PR analysis
- Enable auto-fix to generate patches automatically

---
*Powered by [Semcod](https://semcod.com)*
"""

    return comment


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
