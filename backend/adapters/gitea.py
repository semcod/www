"""Gitea adapter - implementation of GitProvider for Gitea."""
from typing import Dict, Optional

from fastapi import HTTPException

from events.models import Event, EventType, ProviderType
from .base import HttpApiProvider
from .gitea_events import parse_gitea_event


class GiteaAdapter(HttpApiProvider):
    """Gitea API implementation. Inherits ~12 shared methods from HttpApiProvider.

    Gitea API is compatible with GitHub API v3 in most places; only branch creation,
    ref lookup, diff retrieval, and commit statuses differ.
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

    # ─── Branch Operations (Gitea-specific endpoints) ─────────────────────────

    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str:
        url = f"{self.api_base}/repos/{repo}/branches"
        resp = await self._req("POST", url, json={"new_branch_name": branch, "old_branch_name": from_sha})
        if resp.status_code == 409:
            return f"refs/heads/{branch}"
        if resp.status_code not in (200, 201):
            await self._create_branch_via_git(repo, branch, from_sha)
        return f"refs/heads/{branch}"

    async def _create_branch_via_git(self, repo: str, branch: str, from_sha: str) -> None:
        url = f"{self.api_base}/repos/{repo}/git/refs"
        resp = await self._req("POST", url, json={"ref": f"refs/heads/{branch}", "sha": from_sha})
        if resp.status_code not in (200, 201, 422):
            raise HTTPException(500, f"Failed to create branch: {resp.text}")

    async def delete_branch(self, repo: str, branch: str) -> bool:
        url = f"{self.api_base}/repos/{repo}/branches/{branch}"
        resp = await self._req("DELETE", url)
        return resp.status_code == 204

    async def get_ref_sha(self, repo: str, ref: str) -> str:
        url = f"{self.api_base}/repos/{repo}/branches/{ref}"
        resp = await self._req("GET", url)
        if resp.status_code != 200:
            url = f"{self.api_base}/repos/{repo}/git/refs/heads/{ref}"
            resp = await self._req("GET", url)
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref {ref}: {resp.text}")
        data = resp.json()
        if "commit" in data:
            return data["commit"]["id"]
        if "object" in data:
            return data["object"]["sha"]
        return data.get("sha", "")

    # ─── Diff (Gitea uses .diff endpoint) ─────────────────────────────────────

    async def get_pr_diff(self, repo: str, pr_id: int) -> str:
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_id}.diff"
        resp = await self._req("GET", url)
        if resp.status_code == 404:
            raise HTTPException(404, f"PR #{pr_id} not found in {repo}")
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get diff: {resp.status_code} - {resp.text}")
        return resp.text

    # ─── Check Runs (Gitea uses commit status API) ────────────────────────────

    async def create_check_run(
        self, repo: str, name: str, head_sha: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> str:
        state_map = {
            "queued": "pending", "in_progress": "pending",
            "completed": "success" if conclusion == "success" else "failure",
        }
        url = f"{self.api_base}/repos/{repo}/statuses/{head_sha}"
        resp = await self._req("POST", url, json={
            "context": name,
            "state": state_map.get(status, "pending"),
            "description": output.get("title", "Semcod") if output else "Semcod",
            "target_url": output.get("url", "") if output else "",
        })
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create status: {resp.text}")
        return str(resp.json().get("id", head_sha))

    async def update_check_run(
        self, repo: str, check_run_id: str, status: str,
        conclusion: Optional[str] = None, output: Optional[Dict] = None,
    ) -> bool:
        return True
