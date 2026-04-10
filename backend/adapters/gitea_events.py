"""Gitea event parsing utilities."""
from typing import Dict, Optional

from events.models import Event, EventType, ProviderType


def parse_gitea_event(payload: Dict) -> Optional[Event]:
    """Parse Gitea webhook payload into unified Event."""
    event_type = _detect_gitea_event_type(payload)

    repo_data = payload.get("repository", {})
    repo = repo_data.get("full_name")
    if not repo:
        return None

    # Extract PR data
    pr_data = payload.get("pull_request", {})
    pr_id = pr_data.get("number")
    action = payload.get("action")

    # Extract author
    sender = payload.get("sender", {})
    author = sender.get("login")
    author_id = sender.get("id")

    # Get commits if available
    commits = payload.get("commits", [])

    return Event(
        type=event_type,
        provider=ProviderType.GITEA,
        repo=repo,
        pr_id=pr_id,
        branch=pr_data.get("head", {}).get("ref"),
        base_branch=pr_data.get("base", {}).get("ref"),
        diff_url=pr_data.get("diff_url"),
        commit_sha=pr_data.get("head", {}).get("sha"),
        commits=commits,
        author=author,
        author_id=author_id,
        pr_title=pr_data.get("title"),
        pr_body=pr_data.get("body"),
        pr_state=pr_data.get("state"),
        is_draft=pr_data.get("draft", False),
        action=action,
        created_at=pr_data.get("created_at"),
        updated_at=pr_data.get("updated_at"),
        raw_payload=payload,
    )


def _detect_gitea_event_type(payload: Dict) -> EventType:
    """Detect event type from Gitea payload."""
    if "pull_request" in payload:
        return EventType.PULL_REQUEST
    elif "commits" in payload and "ref" in payload:
        return EventType.PUSH
    elif "issue" in payload:
        return EventType.ISSUE
    return EventType.UNKNOWN
