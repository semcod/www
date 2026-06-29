"""Unified webhook handler - multi-platform support via adapters."""

import asyncio
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request

from services.webhook_service import (
    get_adapter_for_event,
    parse_github_webhook,
    parse_gitlab_webhook,
    parse_gitea_webhook,
    process_pr_event,
    process_push_event,
    verify_github_signature,
    verify_gitea_signature,
)
from events.models import Event, EventType, ProviderType

router = APIRouter()

# Keep references to background tasks to prevent garbage collection
_background_tasks = set()


# ─── Webhook Endpoints ──────────────────────────────────────────────────────────


@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events using unified adapter system."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Verify signature if secret configured
    from config import GITHUB_WEBHOOK_SECRET

    if GITHUB_WEBHOOK_SECRET:
        if not verify_github_signature(body, signature, GITHUB_WEBHOOK_SECRET):
            raise HTTPException(401, "Invalid signature")

    payload = await request.json()
    event = parse_github_webhook(payload)

    if not event:
        return {"status": "ignored", "reason": "could not parse event"}

    return await _route_event(event)


@router.post("/webhook/gitlab")
async def gitlab_webhook(request: Request):
    """Handle GitLab webhook events."""
    # GitLab uses X-Gitlab-Token header for verification
    token = request.headers.get("X-Gitlab-Token", "")
    from config import GITLAB_WEBHOOK_SECRET

    if GITLAB_WEBHOOK_SECRET and token != GITLAB_WEBHOOK_SECRET:
        raise HTTPException(401, "Invalid token")

    payload = await request.json()
    event = parse_gitlab_webhook(payload)

    if not event:
        return {"status": "ignored", "reason": "could not parse event"}

    return await _route_event(event)


@router.post("/webhook/gitea")
async def gitea_webhook(request: Request):
    """Handle Gitea webhook events."""
    body = await request.body()
    signature = request.headers.get("X-Gitea-Signature", "")
    gitea_event = request.headers.get("X-Gitea-Event", "")

    from config import GITEA_WEBHOOK_SECRET

    if GITEA_WEBHOOK_SECRET:
        if not verify_gitea_signature(body, signature, GITEA_WEBHOOK_SECRET):
            raise HTTPException(401, "Invalid signature")

    payload = await request.json()
    event = parse_gitea_webhook(payload, gitea_event_header=gitea_event)

    if not event:
        return {"status": "ignored", "reason": "could not parse event"}

    return await _route_event(event)


# ─── Internal Event Routing ─────────────────────────────────────────────────────


async def _route_event(event: Event) -> Dict:
    """Route event to appropriate handler based on type."""
    # Get token for the provider (in real implementation from DB/config)
    token = _get_token_for_provider(event.provider)
    if not token:
        return {"status": "ignored", "reason": "no token configured"}

    provider = get_adapter_for_event(event, token)

    # Route by event type
    if event.type == EventType.PULL_REQUEST:
        task = asyncio.create_task(process_pr_event(event, provider))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        return {"status": "processing", "event": "pull_request"}

    elif event.type == EventType.PUSH:
        task = asyncio.create_task(process_push_event(event, provider))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        return {"status": "processing", "event": "push"}

    return {"status": "ignored", "reason": "unsupported event type"}


def _get_token_for_provider(provider: ProviderType) -> Optional[str]:
    """Get API token for provider from config."""
    from config import GITHUB_TOKEN, GITLAB_TOKEN, GITEA_TOKEN

    token_map = {
        ProviderType.GITHUB: GITHUB_TOKEN,
        ProviderType.GITLAB: GITLAB_TOKEN,
        ProviderType.GITEA: GITEA_TOKEN,
    }
    return token_map.get(provider)
