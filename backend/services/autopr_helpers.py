"""Helper classes for Auto-PR generation - extracted from routers/autopr.py to reduce fan-out."""

import base64
import hashlib
import logging
from datetime import datetime, timezone
from typing import List

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _gh_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


class BranchManager:
    """Manages GitHub branch operations."""

    @staticmethod
    async def get_default_branch(repo: str, token: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{GITHUB_API}/repos/{repo}", headers=_gh_headers(token))
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot access repo {repo}: {resp.text}")
        return resp.json().get("default_branch", "main")

    @staticmethod
    async def get_ref_sha(repo: str, branch: str, token: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/repos/{repo}/git/refs/heads/{branch}",
                headers=_gh_headers(token),
            )
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot get ref for {branch}: {resp.text}")
        return resp.json()["object"]["sha"]

    @staticmethod
    async def create_branch(repo: str, branch: str, sha: str, token: str) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API}/repos/{repo}/git/refs",
                headers=_gh_headers(token),
                json={"ref": f"refs/heads/{branch}", "sha": sha},
            )
        if resp.status_code not in (201, 422):
            raise HTTPException(500, f"Failed to create branch {branch}: {resp.text}")


class PatchApplier:
    """Applies patches to files in a GitHub repository."""

    @staticmethod
    async def get_file_sha(repo: str, path: str, branch: str, token: str) -> str | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/repos/{repo}/contents/{path}",
                headers=_gh_headers(token),
                params={"ref": branch},
            )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(422, f"Cannot read {path}: {resp.text}")
        return resp.json().get("sha")

    @staticmethod
    async def commit_file(
        repo: str,
        path: str,
        content: str,
        branch: str,
        message: str,
        token: str,
        file_sha: str | None,
    ) -> None:
        encoded = base64.b64encode(content.encode()).decode()
        body: dict = {"message": message, "content": encoded, "branch": branch}
        if file_sha:
            body["sha"] = file_sha
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{GITHUB_API}/repos/{repo}/contents/{path}",
                headers=_gh_headers(token),
                json=body,
            )
        if resp.status_code not in (200, 201):
            raise HTTPException(500, f"Failed to commit {path}: {resp.text}")


class PRCreator:
    """Creates GitHub PRs and issues."""

    @staticmethod
    async def create_pr(repo: str, branch: str, base: str, title: str, body: str, token: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API}/repos/{repo}/pulls",
                headers=_gh_headers(token),
                json={"title": title, "body": body, "head": branch, "base": base},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create PR: {resp.text}")
        return resp.json()["html_url"]

    @staticmethod
    async def create_issue(repo: str, title: str, body: str, token: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API}/repos/{repo}/issues",
                headers=_gh_headers(token),
                json={"title": title, "body": body, "labels": ["semcod", "code-quality"]},
            )
        if resp.status_code != 201:
            raise HTTPException(500, f"Failed to create issue: {resp.text}")
        return resp.json()["html_url"]

    @staticmethod
    def build_pr_body(proposal_type: str, fix_id: str, llm_prompt: str, patches: List,
                      score_before: int | None, score_after: int | None) -> str:
        score_section = ""
        if score_before is not None and score_after is not None:
            delta = score_after - score_before
            sign = "+" if delta >= 0 else ""
            score_section = f"\n\n## Health Score\n| Before | After | Delta |\n|--------|-------|-------|\n| {score_before} | {score_after} | {sign}{delta} |\n"

        return f"""## Semcod Auto-Fix

**Fix ID:** `{fix_id}`
**Type:** `{proposal_type}`
{score_section}
## What was changed

{llm_prompt}

## Files modified

{chr(10).join(f'- `{p.path}`' for p in patches)}

---
*Generated by [Semcod](https://semcod.com) — AI-powered code health analysis*
"""

    @staticmethod
    def build_issue_body(proposal_type: str, fix_id: str, reason: str, llm_prompt: str, patches: List,
                         score_before: int | None, score_after: int | None) -> str:
        return f"""## Semcod Auto-Fix Failed

**Fix ID:** `{fix_id}`
**Type:** `{proposal_type}`
**Reason:** {reason}

### Attempted patch

{llm_prompt}

### Files that would have been modified

{chr(10).join(f'- `{p.path}`' for p in patches)}

---
*This issue was created automatically by [Semcod](https://semcod.com)*
"""


def generate_fix_id(repo: str, proposal_type: str) -> str:
    """Generate a unique fix ID for tracking."""
    return hashlib.sha256(
        f"{repo}-{proposal_type}-{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:8]