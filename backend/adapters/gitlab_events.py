"""GitLab webhook event parsing."""

from typing import Dict, Optional

from events.models import Event, EventType, ProviderType


def parse_gitlab_event(payload: Dict) -> Optional[Event]:
    """Parse GitLab webhook payload into unified Event."""
    event_type = _detect_gitlab_event_type(payload)

    # Get project info
    project = payload.get("project", {})
    repo = project.get("path_with_namespace")
    if not repo:
        return None

    # Extract MR data if present
    mr_data = payload.get("object_attributes", {})
    mr_id = mr_data.get("iid")
    action = mr_data.get("action")

    # Extract author
    author_data = payload.get("user", {})
    author = author_data.get("username")
    author_id = author_data.get("id")

    # Get commits from payload if push event
    commits = payload.get("commits", [])

    return Event(
        type=event_type,
        provider=ProviderType.GITLAB,
        repo=repo,
        pr_id=mr_id,
        branch=mr_data.get("source_branch")
        or payload.get("ref", "").replace("refs/heads/", ""),
        base_branch=mr_data.get("target_branch"),
        diff_url=mr_data.get("url"),
        commit_sha=mr_data.get("last_commit", {}).get("id")
        or payload.get("checkout_sha"),
        commits=commits,
        author=author,
        author_id=author_id,
        pr_title=mr_data.get("title"),
        pr_body=mr_data.get("description"),
        pr_state=mr_data.get("state"),
        is_draft=mr_data.get("work_in_progress", False),
        action=action,
        created_at=mr_data.get("created_at"),
        updated_at=mr_data.get("updated_at"),
        raw_payload=payload,
    )


def _detect_gitlab_event_type(payload: Dict) -> EventType:
    """Detect event type from GitLab payload."""
    object_kind = payload.get("object_kind", "")

    if object_kind == "merge_request" or "merge_request" in payload:
        return EventType.PULL_REQUEST
    elif object_kind == "issue":
        return EventType.ISSUE
    elif object_kind == "push" or ("commits" in payload and "ref" in payload):
        return EventType.PUSH
    elif "object_attributes" in payload:
        obj_type = payload["object_attributes"].get("target_type", "")
        if obj_type == "MergeRequest":
            return EventType.PULL_REQUEST
        elif obj_type == "Issue":
            return EventType.ISSUE
    return EventType.UNKNOWN
