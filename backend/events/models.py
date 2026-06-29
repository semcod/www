"""Unified Event Model - platform-agnostic representation of git events."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Supported event types across all platforms."""

    PULL_REQUEST = "pull_request"
    PUSH = "push"
    ISSUE = "issue"
    PULL_REQUEST_COMMENT = "pull_request_comment"
    UNKNOWN = "unknown"


class ProviderType(Enum):
    """Supported git providers."""

    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"
    BITBUCKET = "bitbucket"


@dataclass
class Event:
    """Unified event representation across all git platforms.

    This class normalizes events from GitHub, GitLab, Gitea, etc.
    into a common format that apps can work with.
    """

    # Core identification
    type: EventType
    provider: ProviderType
    repo: str  # full repo name: "owner/repo"

    # PR/Issue specific
    pr_id: Optional[int] = None
    issue_id: Optional[int] = None
    branch: Optional[str] = None
    base_branch: Optional[str] = None

    # Content
    diff: Optional[str] = None
    diff_url: Optional[str] = None
    commit_sha: Optional[str] = None
    commits: List[Dict] = field(default_factory=list)

    # Actor
    author: Optional[str] = None
    author_id: Optional[int] = None

    # PR metadata
    pr_title: Optional[str] = None
    pr_body: Optional[str] = None
    pr_state: Optional[str] = None  # open, closed, merged
    is_draft: bool = False

    # Event metadata
    action: Optional[str] = None  # opened, synchronize, closed, etc.
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Raw payload (for platform-specific access if needed)
    raw_payload: Dict[str, Any] = field(default_factory=dict, repr=False)

    # Installation/app context
    installation_id: Optional[int] = None
    app_id: Optional[str] = None

    def is_pr_event(self) -> bool:
        """Check if this is a pull request event."""
        return self.type == EventType.PULL_REQUEST

    def is_push_event(self) -> bool:
        """Check if this is a push event."""
        return self.type == EventType.PUSH

    def is_comment_event(self) -> bool:
        """Check if this is a comment event."""
        return self.type == EventType.PULL_REQUEST_COMMENT

    def get_pr_url(self) -> Optional[str]:
        """Get PR URL from raw payload if available."""
        if self.provider == ProviderType.GITHUB:
            return self.raw_payload.get("pull_request", {}).get("html_url")
        elif self.provider == ProviderType.GITLAB:
            return self.raw_payload.get("object_attributes", {}).get("url")
        elif self.provider == ProviderType.GITEA:
            return self.raw_payload.get("pull_request", {}).get("html_url")
        return None

    def get_clone_url(self) -> Optional[str]:
        """Get repository clone URL."""
        if self.provider == ProviderType.GITHUB:
            return self.raw_payload.get("repository", {}).get("clone_url")
        elif self.provider == ProviderType.GITLAB:
            return self.raw_payload.get("project", {}).get("git_http_url")
        elif self.provider == ProviderType.GITEA:
            return self.raw_payload.get("repository", {}).get("clone_url")
        return None
