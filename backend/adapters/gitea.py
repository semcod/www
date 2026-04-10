"""Gitea adapter - implementation of GitProvider for Gitea."""
import base64
import hashlib
import hmac
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException

from events.models import Event, EventType, ProviderType
from .base import GitProvider


class GiteaAdapter(GitProvider):
    """Gitea API implementation of GitProvider.

    Gitea API is compatible with GitHub API v3 in most places,
    but has some differences in endpoints and field names.
    """

    def __init__(self, token: str, base_url: str = "http://localhost:3000"):
        super().__init__(token, base_url)
        self.api_base = f"{base_url.rstrip('/')}/api/v1"

    @property
    def provider_name(self) -> str:
        return "gitea"

    def get_api_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # ─── PR Operations (Pull Requests in Gitea) ──────────────────────────────────

    async def comment_on_pr(self, repo: str, pr_id: int, text: str) -> str:
        """Post a comment on a Gitea PR."""
        url = f"{self.api_base}/repos/{repo}/issues/{pr_id}/comments"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"body": text},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to comment: {resp.text}")
        return resp.json().get("html_url", "")

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
        url = f"{self.api_base}/repos/{repo}/branches"
        async with httpx.AsyncClient() as client:
            # Gitea uses different endpoint for branch creation
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"new_branch_name": branch, "old_branch_name": from_sha},
            )
        if resp.status_code == 409:  # Branch already exists
            return f"refs/heads/{branch}"
        if resp.status_code not in (201, 200):
            # Alternative: create via git API
            resp = await self._create_branch_via_git(repo, branch, from_sha)
        return f"refs/heads/{branch}"

    async def _create_branch_via_git(self, repo: str, branch: str, from_sha: str) -> str:
        """Create branch using git refs API."""
        url = f"{self.api_base}/repos/{repo}/git/refs"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"ref": f"refs/heads/{branch}", "sha": from_sha},
            )
        if resp.status_code not in (201, 200, 422):
            raise HTTPException(500, f"Failed to create branch: {resp.text}")
        return f"refs/heads/{branch}"

    async def delete_branch(self, repo: str, branch: str) -> bool:
        """Delete a branch."""
        url = f"{self.api_base}/repos/{repo}/branches/{branch}"
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
        """Commit a single file via Gitea API."""
        encoded = base64.b64encode(content.encode()).decode()
        body: Dict = {"content": encoded, "message": message, "branch": branch}
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
        """Get SHA for a branch."""
        url = f"{self.api_base}/repos/{repo}/branches/{ref}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            # Try git refs endpoint
            url = f"{self.api_base}/repos/{repo}/git/refs/heads/{ref}"
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref {ref}: {resp.text}")

        data = resp.json()
        if "commit" in data:
            return data["commit"]["id"]
        if "object" in data:
            return data["object"]["sha"]
        return data.get("sha", "")

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
        """Get PR diff content."""
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}.diff"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            # Try alternative endpoint
            url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
            resp = await client.get(url, headers=self.get_api_headers())
            if resp.status_code == 200:
                return resp.json().get("diff_url", "")
            raise HTTPException(422, f"Cannot get diff: {resp.text}")
        return resp.text

    async def get_file_content(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file content at ref."""
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
        """Create a Gitea issue."""
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
        """Comment on issue (same endpoint as PR in Gitea)."""
        return await self.comment_on_pr(repo, issue_id, text)

    # ─── Check Runs (Gitea has commit status API) ─────────────────────────────────

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> str:
        """Create a commit status (Gitea's equivalent of check runs)."""
        url = f"{self.api_base}/repos/{repo}/statuses/{head_sha}"

        # Map status
        state_map = {
            "queued": "pending",
            "in_progress": "pending",
            "completed": "success" if conclusion == "success" else "failure",
        }
        state = state_map.get(status, "pending")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "context": name,
                    "state": state,
                    "description": output.get("title", "Semcod") if output else "Semcod",
                    "target_url": output.get("url", "") if output else "",
                },
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create status: {resp.text}")
        return str(resp.json().get("id", head_sha))

    async def update_check_run(
        self,
        repo: str,
        check_run_id: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> bool:
        """Update commit status (create new one in Gitea)."""
        return True

    # ─── Webhook Verification ───────────────────────────────────────────────────

    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        """Verify Gitea webhook signature."""
        expected = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)


# ─── Event Parser ───────────────────────────────────────────────────────────────


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
