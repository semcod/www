"""Gitea event parsing utilities."""
from typing import Dict, Optional

from events.models import Event, EventType, ProviderType


def parse_gitea_event(payload: Dict, gitea_event_header: str = "") -> Optional[Event]:
    """Parse Gitea webhook payload into unified Event."""
    event_type = _detect_gitea_event_type(payload, gitea_event_header)

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


def _detect_gitea_event_type(payload: Dict, gitea_event_header: str = "") -> EventType:
    """Detect event type from Gitea X-Gitea-Event header or payload."""
    header_map = {
        "push": EventType.PUSH,
        "pull_request": EventType.PULL_REQUEST,
        "issues": EventType.ISSUE,
        "issue_comment": EventType.ISSUE,
    }
    if gitea_event_header:
        return header_map.get(gitea_event_header, EventType.UNKNOWN)
    # Fallback to payload inspection
    if "pull_request" in payload:
        return EventType.PULL_REQUEST
    elif "commits" in payload and "ref" in payload:
        return EventType.PUSH
    elif "issue" in payload:
        return EventType.ISSUE
    return EventType.UNKNOWN
