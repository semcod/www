"""GitHub adapter - implementation of GitProvider for GitHub."""
from typing import Dict, Optional

from fastapi import HTTPException

from events.models import Event, EventType, ProviderType
from .base import HttpApiProvider


class GitHubAdapter(HttpApiProvider):
    """GitHub API implementation. Inherits ~12 shared methods from HttpApiProvider."""

    GITHUB_API = "https://api.github.com"

    def __init__(self, token: str, base_url: Optional[str] = None):
        super().__init__(token, base_url)
        self.api_base = base_url or self.GITHUB_API

    @property
    def provider_name(self) -> str:
        return "github"

    def get_api_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ─── Branch Operations (GitHub-specific endpoints) ────────────────────────

    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str:
        url = f"{self.api_base}/repos/{repo}/git/refs"
        resp = await self._req("POST", url, json={"ref": f"refs/heads/{branch}", "sha": from_sha})
        if resp.status_code == 422:
            return f"refs/heads/{branch}"
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create branch: {resp.text}")
        return resp.json()["ref"]

    async def delete_branch(self, repo: str, branch: str) -> bool:
        url = f"{self.api_base}/repos/{repo}/git/refs/heads/{branch}"
        resp = await self._req("DELETE", url)
        return resp.status_code == 204

    async def get_ref_sha(self, repo: str, ref: str) -> str:
        url = f"{self.api_base}/repos/{repo}/git/refs/heads/{ref}"
        resp = await self._req("GET", url)
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref {ref}: {resp.text}")
        return resp.json()["object"]["sha"]

    # ─── Diff (GitHub uses Accept header for raw diff) ────────────────────────

    async def get_pr_diff(self, repo: str, pr_id: int) -> str:
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        resp = await self._req("GET", url, extra_headers={"Accept": "application/vnd.github.diff"})
        if resp.status_code == 404:
            raise HTTPException(404, f"PR #{pr_id} not found in {repo}")
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get diff: {resp.status_code} - {resp.text}")
        return resp.text

    # ─── Check Runs (GitHub-specific) ────────────────────────────────────────

    async def create_check_run(
        self, repo: str, name: str, head_sha: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> str:
        url = f"{self.api_base}/repos/{repo}/check-runs"
        body: Dict = {"name": name, "head_sha": head_sha, "status": status}
        if conclusion:
            body["conclusion"] = conclusion
        if output:
            body["output"] = output
        resp = await self._req("POST", url, json=body)
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create check run: {resp.text}")
        return str(resp.json()["id"])

    async def update_check_run(
        self, repo: str, check_run_id: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> bool:
        url = f"{self.api_base}/repos/{repo}/check-runs/{check_run_id}"
        body: Dict = {"status": status}
        if conclusion:
            body["conclusion"] = conclusion
        if output:
            body["output"] = output
        resp = await self._req("PATCH", url, json=body)
        return resp.status_code == 200

    # ─── Webhook (GitHub prefixes with "sha256=") ─────────────────────────────

    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        import hashlib
        import hmac
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)


# ─── Event Parser ───────────────────────────────────────────────────────────────


def parse_github_event(payload: Dict) -> Optional[Event]:
    """Parse GitHub webhook payload into unified Event."""
    event_type = _detect_github_event_type(payload)

    repo = payload.get("repository", {}).get("full_name")
    if not repo:
        return None

    # Extract PR data if present
    pr_data = payload.get("pull_request", {})
    pr_id = pr_data.get("number")
    action = payload.get("action")

    # Extract author
    sender = payload.get("sender", {})
    author = sender.get("login")
    author_id = sender.get("id")

    # Determine branch based on event type
    branch = None
    base_branch = None
    if event_type == EventType.PUSH:
        ref = payload.get("ref", "")
        branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref
    else:
        branch = pr_data.get("head", {}).get("ref")
        base_branch = pr_data.get("base", {}).get("ref")

    # Build Event
    return Event(
        type=event_type,
        provider=ProviderType.GITHUB,
        repo=repo,
        pr_id=pr_id,
        branch=branch,
        base_branch=base_branch,
        diff_url=pr_data.get("diff_url"),
        commit_sha=pr_data.get("head", {}).get("sha"),
        commits=payload.get("commits", []),
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
        installation_id=payload.get("installation", {}).get("id"),
    )


def _detect_github_event_type(payload: Dict) -> EventType:
    """Detect event type from GitHub payload structure."""
    if "pull_request" in payload:
        return EventType.PULL_REQUEST
    elif "pusher" in payload and "ref" in payload:
        return EventType.PUSH
    elif "issue" in payload and "pull_request" not in payload.get("issue", {}):
        return EventType.ISSUE
    return EventType.UNKNOWN
