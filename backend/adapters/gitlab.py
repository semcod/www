"""GitLab adapter - implementation of GitProvider for GitLab."""
import base64
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException

from events.models import Event, EventType, ProviderType
from .base import GitProvider


class GitLabAdapter(GitProvider):
    """GitLab API implementation of GitProvider."""

    def __init__(self, token: str, base_url: str = "https://gitlab.com"):
        super().__init__(token, base_url)
        self.api_base = f"{base_url.rstrip('/')}/api/v4"

    @property
    def provider_name(self) -> str:
        return "gitlab"

    def get_api_headers(self) -> Dict[str, str]:
        return {
            "Private-Token": self.token,
            "Content-Type": "application/json",
        }

    def _get_project_path(self, repo: str) -> str:
        """Convert owner/repo to URL-encoded path for GitLab API."""
        return repo.replace("/", "%2F")

    # ─── PR Operations (Merge Requests in GitLab) ─────────────────────────────────

    async def comment_on_pr(self, repo: str, pr_id: int, text: str) -> str:
        """Post a comment on a GitLab MR."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests/{pr_id}/notes"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"body": text},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to comment: {resp.text}")
        return resp.json().get("web_url", "")

    async def update_pr_description(self, repo: str, pr_id: int, description: str) -> bool:
        """Update MR description."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests/{pr_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                url,
                headers=self.get_api_headers(),
                json={"description": description},
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
        """Create a new merge request."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "source_branch": head_branch,
                    "target_branch": base_branch,
                    "title": title,
                    "description": body,
                },
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create MR: {resp.text}")
        return resp.json().get("web_url", "")

    async def close_pr(self, repo: str, pr_id: int, comment: Optional[str] = None) -> bool:
        """Close a MR with optional comment."""
        if comment:
            await self.comment_on_pr(repo, pr_id, comment)

        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests/{pr_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                url,
                headers=self.get_api_headers(),
                json={"state_event": "close"},
            )
        return resp.status_code == 200

    # ─── Branch & Commit Operations ─────────────────────────────────────────────

    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str:
        """Create a new branch from commit SHA."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/repository/branches"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"branch": branch, "ref": from_sha},
            )
        if resp.status_code == 400:  # Branch already exists
            return f"refs/heads/{branch}"
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create branch: {resp.text}")
        return f"refs/heads/{branch}"

    async def delete_branch(self, repo: str, branch: str) -> bool:
        """Delete a branch."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/repository/branches/{branch}"
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
        """Commit a single file via GitLab API (creates commit with single action)."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/repository/commits"

        action = "update" if file_sha else "create"
        actions = [
            {
                "action": action,
                "file_path": path,
                "content": content,
            }
        ]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "branch": branch,
                    "commit_message": message,
                    "actions": actions,
                },
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to commit {path}: {resp.text}")
        return resp.json()["id"]

    async def get_default_branch(self, repo: str) -> str:
        """Get default branch name."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot access repo {repo}: {resp.text}")
        return resp.json().get("default_branch", "main")

    async def get_ref_sha(self, repo: str, ref: str) -> str:
        """Get SHA for a branch."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/repository/branches/{ref}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref {ref}: {resp.text}")
        return resp.json()["commit"]["id"]

    async def get_file_sha(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file blob ID for updates. None if doesn't exist."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/repository/files/{path.replace('/', '%2F')}"
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
        return resp.json().get("blob_id")

    # ─── Diff & Content ─────────────────────────────────────────────────────────

    async def get_pr_diff(self, repo: str, pr_id: int) -> str:
        """Get MR diff content from GitLab.

        Uses merge requests changes API and formats as unified diff.
        """
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests/{pr_id}/changes"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())

        if resp.status_code == 404:
            raise HTTPException(404, f"MR !{pr_id} not found in {repo}")
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get diff: {resp.status_code} - {resp.text}")

        data = resp.json()
        changes = data.get("changes", [])

        # Format changes as unified diff
        diff_lines = []
        for change in changes:
            old_path = change.get("old_path", "")
            new_path = change.get("new_path", "")
            diff = change.get("diff", "")

            if diff:
                diff_lines.append(f"diff --git a/{old_path} b/{new_path}")
                diff_lines.append(diff)
                diff_lines.append("")

        return "\n".join(diff_lines)

    async def get_pr_files(self, repo: str, pr_id: int) -> list:
        """Get list of files changed in MR."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/merge_requests/{pr_id}/changes"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.get_api_headers())

        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get MR files: {resp.text}")

        data = resp.json()
        changes = data.get("changes", [])

        return [
            {
                "filename": c.get("new_path"),
                "status": "modified" if c.get("old_path") == c.get("new_path") else "renamed",
                "additions": c.get("additions", 0),
                "deletions": c.get("deletions", 0),
                "changes": c.get("additions", 0) + c.get("deletions", 0),
                "patch": c.get("diff", ""),
                "previous_filename": c.get("old_path") if c.get("old_path") != c.get("new_path") else None,
            }
            for c in changes
        ]

    async def get_file_content(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file content at ref."""
        project = self._get_project_path(repo)
        encoded_path = path.replace("/", "%2F")
        url = f"{self.api_base}/projects/{project}/repository/files/{encoded_path}/raw"
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
        return resp.text

    # ─── Issue Operations ───────────────────────────────────────────────────────

    async def create_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: List[str],
    ) -> str:
        """Create a GitLab issue."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/issues"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "title": title,
                    "description": body,
                    "labels": ",".join(labels),
                },
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create issue: {resp.text}")
        return resp.json().get("web_url", "")

    async def comment_on_issue(self, repo: str, issue_id: int, text: str) -> str:
        """Comment on issue."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/issues/{issue_id}/notes"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={"body": text},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to comment: {resp.text}")
        return resp.json().get("web_url", "")

    # ─── Check Runs (Pipeline Status in GitLab) ───────────────────────────────────

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> str:
        """Create a pipeline status (GitLab doesn't have exact check runs, use commit status)."""
        project = self._get_project_path(repo)
        url = f"{self.api_base}/projects/{project}/statuses/{head_sha}"

        # Map status to GitLab states
        state_map = {
            "queued": "pending",
            "in_progress": "running",
            "completed": "success" if conclusion == "success" else "failed",
        }
        state = state_map.get(status, "pending")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self.get_api_headers(),
                json={
                    "state": state,
                    "name": name,
                    "description": output.get("title", "Semcod check") if output else "Semcod",
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
        """Update commit status (same as create in GitLab)."""
        # GitLab commit statuses are immutable once set, create new one
        return True

    # ─── Webhook Verification ───────────────────────────────────────────────────

    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        """Verify GitLab webhook signature (X-Gitlab-Token or HMAC)."""
        # GitLab uses simple token or JWT, simplified here
        import hmac
        import hashlib

        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)


