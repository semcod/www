"""Unified webhook handler - multi-platform support via adapters."""
import asyncio
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request

from adapters import (
    GitHubAdapter,
    GitLabAdapter,
    GiteaAdapter,
    parse_github_event,
    parse_gitlab_event,
    parse_gitea_event,
)
from adapters.base import GitProvider
from events.models import Event, EventType, ProviderType

router = APIRouter()

# Keep references to background tasks to prevent garbage collection
_background_tasks = set()


def get_adapter_for_event(event: Event, token: str) -> GitProvider:
    """Factory function - get appropriate adapter for event provider."""
    if event.provider == ProviderType.GITHUB:
        return GitHubAdapter(token)
    elif event.provider == ProviderType.GITLAB:
        return GitLabAdapter(token)
    elif event.provider == ProviderType.GITEA:
        # Try to get base URL from raw payload or use default
        base_url = event.raw_payload.get("repository", {}).get("html_url", "").replace(f"/{event.repo}", "")
        return GiteaAdapter(token, base_url or "http://localhost:3000")
    raise ValueError(f"Unknown provider: {event.provider}")


async def process_pr_event(event: Event, provider: GitProvider) -> Dict:
    """Process pull request event - audit repo and comment results."""
    # Run audit (simplified - in real implementation this calls analysis)
    # For now just acknowledge with comment

    comment = f"""👋 Thanks for the PR, @{event.author}!

🔍 **Semcod** will analyze this PR for code health issues.

Event: {event.action}
Branch: `{event.branch}` → `{event.base_branch}`
"""

    if event.pr_id:
        await provider.comment_on_pr(event.repo, event.pr_id, comment)

    return {
        "status": "processed",
        "repo": event.repo,
        "pr_id": event.pr_id,
        "action": event.action,
    }


async def process_push_event(event: Event, provider: GitProvider) -> Dict:
    """Process push event - trigger analysis if main branch."""
    # Only process pushes to default branch
    if event.branch in ("main", "master"):
        return {
            "status": "analysis_scheduled",
            "repo": event.repo,
            "branch": event.branch,
            "commits": len(event.commits),
        }

    return {"status": "ignored", "reason": "not default branch"}


# ─── Webhook Endpoints ──────────────────────────────────────────────────────────


@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events using unified adapter system."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Verify signature if secret configured
    from config import GITHUB_WEBHOOK_SECRET

    if GITHUB_WEBHOOK_SECRET:
        adapter = GitHubAdapter("")  # Dummy token for verification
        if not adapter.verify_webhook_signature(body, signature, GITHUB_WEBHOOK_SECRET):
            raise HTTPException(401, "Invalid signature")

    payload = await request.json()
    event = parse_github_event(payload)

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
    event = parse_gitlab_event(payload)

    if not event:
        return {"status": "ignored", "reason": "could not parse event"}

    return await _route_event(event)


@router.post("/webhook/gitea")
async def gitea_webhook(request: Request):
    """Handle Gitea webhook events."""
    body = await request.body()
    signature = request.headers.get("X-Gitea-Signature", "")

    from config import GITEA_WEBHOOK_SECRET

    if GITEA_WEBHOOK_SECRET:
        adapter = GiteaAdapter("")  # Dummy token for verification
        if not adapter.verify_webhook_signature(body, signature, GITEA_WEBHOOK_SECRET):
            raise HTTPException(401, "Invalid signature")

    payload = await request.json()
    event = parse_gitea_event(payload)

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
