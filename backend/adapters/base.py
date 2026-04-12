"""Base interface for git providers - PR Bot abstraction."""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException


class GitProvider(ABC):
    """Abstract base class for git platform integrations.

    Provides unified interface for common operations across
    GitHub, GitLab, Gitea, and Bitbucket.
    """

    def __init__(self, token: str, base_url: Optional[str] = None):
        self.token = token
        self.base_url = base_url


class HttpApiProvider(GitProvider):
    """Mixin for providers whose API closely follows the GitHub REST v3 shape.

    GitHub and Gitea share the same endpoint structure under /repos/{owner}/{repo}/
    so the ~12 common methods live here. Subclasses only override the handful of
    methods that actually differ (branch creation, diff, check-runs, etc.).

    Subclasses MUST set ``self.api_base`` in ``__init__`` before use.
    """

    # ─── Low-level HTTP helper ────────────────────────────────────────────────

    async def _req(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        extra_headers: Optional[Dict] = None,
    ) -> httpx.Response:
        headers = {**self.get_api_headers(), **(extra_headers or {})}
        async with httpx.AsyncClient() as client:
            return await client.request(
                method, url, headers=headers, json=json, params=params
            )

    # ─── PR Operations ────────────────────────────────────────────────────────

    async def comment_on_pr(self, repo: str, pr_id: int, text: str) -> str:
        url = f"{self.api_base}/repos/{repo}/issues/{pr_id}/comments"
        resp = await self._req("POST", url, json={"body": text})
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to comment: {resp.text}")
        return resp.json().get("html_url", "")

    async def update_pr_description(self, repo: str, pr_id: int, description: str) -> bool:
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        resp = await self._req("PATCH", url, json={"body": description})
        return resp.status_code == 200

    async def create_pr(
        self, repo: str, title: str, body: str, head_branch: str, base_branch: str,
    ) -> str:
        url = f"{self.api_base}/repos/{repo}/pulls"
        resp = await self._req("POST", url, json={
            "title": title, "body": body, "head": head_branch, "base": base_branch,
        })
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create PR: {resp.text}")
        return resp.json()["html_url"]

    async def close_pr(self, repo: str, pr_id: int, comment: Optional[str] = None) -> bool:
        if comment:
            await self.comment_on_pr(repo, pr_id, comment)
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}"
        resp = await self._req("PATCH", url, json={"state": "closed"})
        return resp.status_code == 200

    # ─── Commit & Content Operations ──────────────────────────────────────────

    async def commit_file(
        self, repo: str, path: str, content: str, branch: str, message: str,
        file_sha: Optional[str] = None,
    ) -> str:
        encoded = base64.b64encode(content.encode()).decode()
        body: Dict = {"message": message, "content": encoded, "branch": branch}
        if file_sha:
            body["sha"] = file_sha
        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        resp = await self._req("PUT", url, json=body)
        if resp.status_code not in (200, 201):
            raise HTTPException(500, f"Failed to commit {path}: {resp.text}")
        return resp.json()["commit"]["sha"]

    async def get_default_branch(self, repo: str) -> str:
        url = f"{self.api_base}/repos/{repo}"
        resp = await self._req("GET", url)
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot access repo {repo}: {resp.text}")
        return resp.json().get("default_branch", "main")

    async def get_file_sha(self, repo: str, path: str, ref: str) -> Optional[str]:
        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        resp = await self._req("GET", url, params={"ref": ref})
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot read {path}: {resp.text}")
        return resp.json().get("sha")

    async def get_file_content(self, repo: str, path: str, ref: str) -> Optional[str]:
        url = f"{self.api_base}/repos/{repo}/contents/{path}"
        resp = await self._req("GET", url, params={"ref": ref})
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot read {path}: {resp.text}")
        return base64.b64decode(resp.json().get("content", "")).decode()

    # ─── Issue Operations ─────────────────────────────────────────────────────

    async def create_issue(self, repo: str, title: str, body: str, labels: List[str]) -> str:
        url = f"{self.api_base}/repos/{repo}/issues"
        resp = await self._req("POST", url, json={"title": title, "body": body, "labels": labels})
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create issue: {resp.text}")
        return resp.json()["html_url"]

    async def comment_on_issue(self, repo: str, issue_id: int, text: str) -> str:
        return await self.comment_on_pr(repo, issue_id, text)

    # ─── PR Files ─────────────────────────────────────────────────────────────

    async def get_pr_files(self, repo: str, pr_id: int) -> list:
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}/files"
        resp = await self._req("GET", url)
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get PR files: {resp.text}")
        return [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "changes": f.get("changes", 0),
                "patch": f.get("patch"),
                "previous_filename": f.get("previous_filename"),
            }
            for f in resp.json()
        ]

    # ─── Webhook Verification ─────────────────────────────────────────────────

    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        expected = _hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return _hmac.compare_digest(signature, expected)

    # ─── Stubs for provider-specific methods ─────────────────────────────────

    @abstractmethod
    def get_api_headers(self) -> Dict[str, str]: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str: ...

    @abstractmethod
    async def delete_branch(self, repo: str, branch: str) -> bool: ...

    @abstractmethod
    async def get_ref_sha(self, repo: str, ref: str) -> str: ...

    @abstractmethod
    async def get_pr_diff(self, repo: str, pr_id: int) -> str: ...

    @abstractmethod
    async def create_check_run(
        self, repo: str, name: str, head_sha: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> str: ...

    @abstractmethod
    async def update_check_run(
        self, repo: str, check_run_id: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> bool: ...
