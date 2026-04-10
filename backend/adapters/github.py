"""GitHub adapter - implementation of GitProvider for GitHub."""
import base64
import hashlib
import hmac
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException

from events.models import Event, EventType, ProviderType
from .base import GitProvider


class GitHubAdapter(GitProvider):
    """GitHub API implementation of GitProvider."""

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

    # ─── PR Operations ──────────────────────────────────────────────────────────

    async def comment_on_pr(self, repo: str, pr_id: int, text: str) -> str:
        """Post a comment on a GitHub PR (uses issues endpoint)."""
        url = f"{self.api_base}/repos/{repo}/issues/{pr_id}/comments"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"body": text},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to comment: {resp.text}")
        return resp.json()["html_url"]

    async def update_pr_description(self, repo: str, pr_id: int, description: str) -> bool:
        """Update PR body/description."""
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                url,
                headers=self.get_api_headers(),
                json={"body": description},
            )
        return resp.status_code == 200

    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
    ) -> str:
        """Create a new pull request."""
        url = f"{self.api_base}/repos/{repo}/pulls"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "title": title,
                    "body": body,
                    "head": head_branch,
                    "base": base_branch,
                },
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create PR: {resp.text}")
        return resp.json()["html_url"]

    async def close_pr(self, repo: str, pr_id: int, comment: Optional[str] = None) -> bool:
        """Close a PR with optional comment."""
        if comment:
            await self.comment_on_pr(repo, pr_id, comment)

        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                url,
                headers=self.get_api_headers(),
                json={"state": "closed"},
            )
        return resp.status_code == 200

    # ─── Branch & Commit Operations ─────────────────────────────────────────────

    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str:
        """Create a new branch from SHA."""
        url = f"{self.api_base}/repos/{repo}/git/refs"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"ref": f"refs/heads/{branch}", "sha": from_sha},
            )
        if resp.status_code == 422:  # Branch already exists
            return f"refs/heads/{branch}"
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create branch: {resp.text}")
        return resp.json()["ref"]

    async def delete_branch(self, repo: str, branch: str) -> bool:
        """Delete a branch."""
        url = f"{self.api_base}/repos/{repo}/git/refs/heads/{branch}"
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, headers=self.get_api_headers())
        return resp.status_code == 204

    async def commit_file(
        self,
        repo: str,
        path: str,
        content: str,
        branch: str,
        message: str,
        file_sha: Optional[str] = None,
    ) -> str:
        """Commit a single file via GitHub API."""
        encoded = base64.b64encode(content.encode()).decode()
        body: Dict = {"message": message, "content": encoded, "branch": branch}
        if file_sha:
            body["sha"] = file_sha

        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.put(url, headers=self.get_api_headers(), json=body)
        if resp.status_code not in (200, 201):
            raise HTTPException(500, f"Failed to commit {path}: {resp.text}")
        return resp.json()["commit"]["sha"]

    async def get_default_branch(self, repo: str) -> str:
        """Get default branch name."""
        url = f"{self.api_base}/repos/{repo}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot access repo {repo}: {resp.text}")
        return resp.json().get("default_branch", "main")

    async def get_ref_sha(self, repo: str, ref: str) -> str:
        """Get SHA for a ref."""
        url = f"{self.api_base}/repos/{repo}/git/refs/heads/{ref}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref {ref}: {resp.text}")
        return resp.json()["object"]["sha"]

    async def get_file_sha(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file SHA for updates. None if doesn't exist."""
        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self.get_api_headers(),
                params={"ref": ref},
            )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot read {path}: {resp.text}")
        return resp.json().get("sha")

    # ─── Diff & Content ─────────────────────────────────────────────────────────

    async def get_pr_diff(self, repo: str, pr_id: int) -> str:
        """Get PR diff content from GitHub.

        Uses GitHub's .diff media type to get raw diff output.
        """
        # GitHub provides .diff format via Accept header or .diff extension
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        headers = {
            **self.get_api_headers(),
            "Accept": "application/vnd.github.diff",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code == 404:
            raise HTTPException(404, f"PR #{pr_id} not found in {repo}")
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get diff: {resp.status_code} - {resp.text}")

        return resp.text

    async def get_pr_files(self, repo: str, pr_id: int) -> list:
        """Get list of files changed in PR with patch data."""
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}/files"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())

        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get PR files: {resp.text}")

        files = resp.json()
        return [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),  # added, removed, modified
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "changes": f.get("changes", 0),
                "patch": f.get("patch"),  # Actual diff patch (may be truncated)
                "previous_filename": f.get("previous_filename"),
            }
            for f in files
        ]

    async def get_file_content(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file content at ref."""
        import base64

        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self.get_api_headers(),
                params={"ref": ref},
            )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot read {path}: {resp.text}")
        content = resp.json().get("content", "")
        return base64.b64decode(content).decode()

    # ─── Issue Operations ───────────────────────────────────────────────────────

    async def create_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: List[str],
    ) -> str:
        """Create a GitHub issue."""
        url = f"{self.api_base}/repos/{repo}/issues"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"title": title, "body": body, "labels": labels},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create issue: {resp.text}")
        return resp.json()["html_url"]

    async def comment_on_issue(self, repo: str, issue_id: int, text: str) -> str:
        """Comment on issue (same as PR comment)."""
        return await self.comment_on_pr(repo, issue_id, text)

    # ─── Check Runs ───────────────────────────────────────────────────────────────

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> str:
        """Create a check run (GitHub-specific)."""
        url = f"{self.api_base}/repos/{repo}/check-runs"
        body: Dict = {"name": name, "head_sha": head_sha, "status": status}
        if conclusion:
            body["conclusion"] = conclusion
        if output:
            body["output"] = output

        headers = {**self.get_api_headers(), "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=body)
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create check run: {resp.text}")
        return str(resp.json()["id"])

    async def update_check_run(
        self,
        repo: str,
        check_run_id: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> bool:
        """Update a check run."""
        url = f"{self.api_base}/repos/{repo}/check-runs/{check_run_id}"
        body: Dict = {"status": status}
        if conclusion:
            body["conclusion"] = conclusion
        if output:
            body["output"] = output

        headers = {**self.get_api_headers(), "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(url, headers=headers, json=body)
        return resp.status_code == 200

    # ─── Webhook Verification ───────────────────────────────────────────────────

    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        """Verify GitHub webhook signature."""
        expected = "sha256=" + hmac.new(
            secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
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
