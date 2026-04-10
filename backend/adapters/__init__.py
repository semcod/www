"""Adapters module - multi-platform git provider support."""
from events.models import Event, ProviderType

from .base import GitProvider
from .github import GitHubAdapter, parse_github_event
from .gitlab import GitLabAdapter
from .gitlab_events import parse_gitlab_event
from .gitea import GiteaAdapter, parse_gitea_event


def get_adapter_for_event(event: Event, token: str) -> GitProvider:
    """Factory function - get appropriate adapter for event provider."""
    if event.provider == ProviderType.GITHUB:
        return GitHubAdapter(token)
    elif event.provider == ProviderType.GITLAB:
        return GitLabAdapter(token)
    elif event.provider == ProviderType.GITEA:
        base_url = event.raw_payload.get("repository", {}).get("html_url", "").replace(
            f"/{event.repo}", ""
        )
        return GiteaAdapter(token, base_url or "http://localhost:3000")
    raise ValueError(f"Unknown provider: {event.provider}")


__all__ = [
    "GitProvider",
    "GitHubAdapter",
    "GitLabAdapter",
    "GiteaAdapter",
    "parse_github_event",
    "parse_gitlab_event",
    "parse_gitea_event",
    "get_adapter_for_event",
]
