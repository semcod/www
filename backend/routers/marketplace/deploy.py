"""Marketplace deploy endpoints - auto-fix and deployment."""
from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from routers.marketplace.models import AutoFixRequest, AutoFixResponse

router = APIRouter(tags=["marketplace"])


def _get_user_token(user: dict) -> str:
    """Get git provider token from user."""
    return user.get("github_token") or user.get("gitlab_token") or user.get("gitea_token")


def _get_provider_user_id(user: dict) -> str:
    """Get provider user ID from user."""
    return str(user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id"))


def _check_billing_limit(tenant_id: int, usage_tracker, event_type) -> tuple[bool, str]:
    """Check if billing allows execution."""
    return usage_tracker.check_can_execute(
        tenant_id=tenant_id,
        event_type=event_type,
        quantity=1,
    )


def _record_billing_usage(tenant_id: int, usage_tracker, event_type, metadata: dict):
    """Record billing usage."""
    try:
        usage_tracker.record_usage(
            tenant_id=tenant_id,
            event_type=event_type,
            quantity=1,
            metadata=metadata,
        )
    except Exception as e:
        print(f"[autofix] Failed to record usage: {e}")


async def _handle_mirror_if_requested(request: AutoFixRequest, user: dict) -> str | None:
    """Handle mirror to Gitea if requested."""
    if not request.mirror_to_gitea or not request.gitea_target_repo:
        return None
    
    try:
        from services.mirror import MirrorService, MirrorConfig

        gitea_token = user.get("gitea_token") or "gitea"
        mirror_service = MirrorService(
            github_token=user.get("github_token"),
            gitlab_token=user.get("gitlab_token"),
            gitea_token=gitea_token,
        )

        mirror_config = MirrorConfig(
            source_repo=request.repo,
            source_provider=request.provider,
            target_repo=request.gitea_target_repo,
            auto_deploy=request.auto_deploy,
        )

        mirror_result = await mirror_service.sync_mirror(mirror_config)
        print(f"[autofix] Mirror status: {mirror_result.status}")
        return mirror_result.status
    except Exception as e:
        print(f"[autofix] Mirror failed: {e}")
        return None


@router.post("/autofix", response_model=AutoFixResponse)
async def trigger_auto_fix(
    request: AutoFixRequest,
    user: dict = Depends(get_current_user),
) -> AutoFixResponse:
    """Trigger auto-fix PR generation for a repository."""
    from database import get_or_create_tenant
    from services.billing import get_usage_tracker, BillingEventType
    token = _get_user_token(user)
    if not token:
        raise HTTPException(401, "Git provider token required")

    # Get tenant
    provider_user_id = _get_provider_user_id(user)
    tenant = get_or_create_tenant(
        provider=request.provider,
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
    )

    # Check billing
    usage_tracker = get_usage_tracker()
    can_execute, reason = _check_billing_limit(tenant["id"], usage_tracker, BillingEventType.AUTOFIX_RUN)

    if not can_execute:
        raise HTTPException(402, reason)

    # Record usage
    _record_billing_usage(
        tenant["id"],
        usage_tracker,
        BillingEventType.AUTOFIX_RUN,
        {"repo": request.repo, "pr_id": request.pr_id},
    )

    # Mirror to Gitea if requested
    mirror_status = await _handle_mirror_if_requested(request, user)

    # Queue task
    from worker.tasks import create_auto_fix_pr
    task = create_auto_fix_pr.delay(
        repo=request.repo,
        base_branch=request.base_branch,
        files=[],
        issues=[],
        proposal_type="auto_fix",
        provider_type=request.provider,
        tenant_id=tenant["id"],
    )

    return AutoFixResponse(
        status="queued",
        message=f"Auto-fix queued. {reason}",
        task_id=task.id,
    )
