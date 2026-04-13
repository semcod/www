"""Webhook service - facade over git adapters for webhook handling."""

from typing import Dict, Optional

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
    """Process push event - trigger reDSL quality loop if main branch."""
    # Only process pushes to default branch
    if event.branch not in ("main", "master"):
        return {"status": "ignored", "reason": "not default branch"}

    # Trigger quality loop via Celery task
    try:
        from worker.tasks.quality_loop import task_on_push_quality_loop

        # Derive local project path from repo name
        project_path = f"/tmp/local-git-repos/{event.repo.replace('/', '_')}"

        # Resolve provider token for PR creation
        token = getattr(provider, "token", "") or ""

        task_on_push_quality_loop.delay(
            repo=event.repo,
            commit_sha=event.commit_sha or "",
            project_path=project_path,
            token=token,
            provider=event.provider.value,
        )
    except Exception:
        pass  # Celery unavailable — graceful degradation

    return {
        "status": "quality_loop_triggered",
        "repo": event.repo,
        "branch": event.branch,
        "commits": len(event.commits),
    }


def parse_github_webhook(payload: dict) -> Optional[Event]:
    """Parse GitHub webhook payload into Event."""
    return parse_github_event(payload)


def parse_gitlab_webhook(payload: dict) -> Optional[Event]:
    """Parse GitLab webhook payload into Event."""
    return parse_gitlab_event(payload)


def parse_gitea_webhook(payload: dict, gitea_event_header: str = "") -> Optional[Event]:
    """Parse Gitea webhook payload into Event."""
    return parse_gitea_event(payload, gitea_event_header=gitea_event_header)


def verify_github_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    adapter = GitHubAdapter("")  # Dummy token for verification
    return adapter.verify_webhook_signature(body, signature, secret)


def verify_gitea_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify Gitea webhook signature."""
    adapter = GiteaAdapter("")  # Dummy token for verification
    return adapter.verify_webhook_signature(body, signature, secret)
