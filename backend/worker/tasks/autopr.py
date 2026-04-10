"""PR generation Celery tasks - auto-PR and auto-fix."""
import asyncio
from typing import Dict, Any, List

try:
    from celery import shared_task
    from celery.exceptions import MaxRetriesExceededError
    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task, MaxRetriesExceededError  # type: ignore[assignment]

from adapters.github import GitHubAdapter
from adapters.gitlab import GitLabAdapter
from adapters.gitea import GiteaAdapter
from events.models import ProviderType


@shared_task(bind=True, max_retries=2)
def create_auto_pr(
    self,
    repo: str,
    base_branch: str,
    patches: list,
    proposal_type: str,
    llm_prompt: str,
    token: str,
    provider_type: str = "github",
) -> Dict[str, Any]:
    """
    Create automated PR with fixes asynchronously.

    Similar to autopr router but as async task.
    """
    try:
        # Get adapter (imports at module level)
        adapter_map = {
            "github": GitHubAdapter,
            "gitlab": GitLabAdapter,
            "gitea": GiteaAdapter,
        }
        adapter_class = adapter_map.get(provider_type, GitHubAdapter)
        adapter = adapter_class(token)

        # Create branch and commit patches
        default_branch = asyncio.run(adapter.get_default_branch(repo))
        base_sha = asyncio.run(adapter.get_ref_sha(repo, default_branch))

        import hashlib
        from datetime import datetime, timezone

        fix_id = hashlib.sha256(
            f"{repo}-{proposal_type}-{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:8]
        branch = f"semcod-fix-{fix_id}"

        asyncio.run(adapter.create_branch(repo, branch, base_sha))

        # Commit each patch
        for patch in patches:
            file_sha = asyncio.run(
                adapter.get_file_sha(repo, patch["path"], branch)
            )
            asyncio.run(
                adapter.commit_file(
                    repo,
                    patch["path"],
                    patch["content"],
                    branch,
                    f"fix({proposal_type}): auto-fix via Semcod [{fix_id}]",
                    file_sha,
                )
            )

        # Create PR
        pr_url = asyncio.run(
            adapter.create_pr(
                repo,
                f"[Semcod] Auto-fix: {proposal_type.replace('_', ' ')} [{fix_id}]",
                f"Auto-fix generated from: {llm_prompt}",
                branch,
                base_branch,
            )
        )

        return {
            "status": "created",
            "repo": repo,
            "pr_url": pr_url,
            "branch": branch,
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60)
        return {
            "status": "failed",
            "error": str(exc),
        }


@shared_task(bind=True, max_retries=2)
def create_auto_fix_pr(
    self,
    repo: str,
    base_branch: str,
    files: List[Dict],
    issues: List[Dict],
    proposal_type: str,
    provider_type: str,
    tenant_id: int,
) -> Dict[str, Any]:
    """
    Create automated PR with fixes asynchronously.

    This is the monetization feature - auto-fix PR generation.
    """
    try:
        from services.autofix import AutoFixService, FixResult
        from database import get_tenant_by_id

        # Get tenant for token
        tenant = get_tenant_by_id(tenant_id)
        if not tenant:
            return {"status": "failed", "error": "Tenant not found"}

        # Get token
        token = _get_token_for_provider(ProviderType(provider_type))
        if not token:
            return {"status": "failed", "error": "No token configured"}

        # Get adapter
        adapter_map = {
            "github": GitHubAdapter,
            "gitlab": GitLabAdapter,
            "gitea": GiteaAdapter,
        }
        adapter_class = adapter_map.get(provider_type, GitHubAdapter)
        adapter = adapter_class(token)

        # Create auto-fix service
        service = AutoFixService(adapter, token)

        # Run auto-fix
        result: FixResult = asyncio.run(
            service.create_auto_fix_pr(
                repo=repo,
                base_branch=base_branch,
                files=files,
                issues=issues,
                proposal_type=proposal_type,
            )
        )

        return {
            "status": result.status,
            "repo": repo,
            "patches_generated": result.patches_generated,
            "patches_applied": result.patches_applied,
            "branch": result.branch,
            "pr_url": result.pr_url,
            "error": result.error,
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60)
        return {
            "status": "failed",
            "error": str(exc),
        }


def _get_token_for_provider(provider: ProviderType) -> str:
    """Get API token for provider from config."""
    import os

    token_map = {
        ProviderType.GITHUB: os.getenv("GITHUB_TOKEN", os.getenv("GITHUB_CLIENT_SECRET", "")),
        ProviderType.GITLAB: os.getenv("GITLAB_TOKEN", ""),
        ProviderType.GITEA: os.getenv("GITEA_TOKEN", ""),
    }
    return token_map.get(provider, "")
