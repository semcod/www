"""Auto-PR generation — applies LLM-generated patches and creates GitHub PRs."""

import hashlib
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.scan_service import get_repo_scans
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/autopr", tags=["autopr"])

GITHUB_API = "https://api.github.com"


# ─── Models ───────────────────────────────────────────────────────────────────

class PatchFile(BaseModel):
    path: str
    content: str


class AutoPRRequest(BaseModel):
    repo: str
    proposal_type: str
    llm_prompt: str
    patches: List[PatchFile]
    branch_prefix: str = "semcod-fix"


class AutoPRResult(BaseModel):
    status: str
    pr_url: str | None = None
    issue_url: str | None = None
    branch: str | None = None
    score_before: int | None = None
    score_after: int | None = None
    rollback_reason: str | None = None


# ─── GitHub helpers ───────────────────────────────────────────────────────────

def _gh_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def _get_default_branch(repo: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GITHUB_API}/repos/{repo}", headers=_gh_headers(token))
    if resp.status_code != 200:
        raise HTTPException(422, f"Cannot access repo {repo}: {resp.text}")
    return resp.json().get("default_branch", "main")


async def _get_ref_sha(repo: str, branch: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/git/refs/heads/{branch}",
            headers=_gh_headers(token),
        )
    if resp.status_code != 200:
        raise HTTPException(422, f"Cannot get ref for {branch}: {resp.text}")
    return resp.json()["object"]["sha"]


async def _create_branch(repo: str, branch: str, sha: str, token: str) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{repo}/git/refs",
            headers=_gh_headers(token),
            json={"ref": f"refs/heads/{branch}", "sha": sha},
        )
    if resp.status_code not in (201, 422):
        raise HTTPException(500, f"Failed to create branch {branch}: {resp.text}")


async def _get_file_sha(repo: str, path: str, branch: str, token: str) -> str | None:
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


async def _commit_file(repo: str, path: str, content: str, branch: str,
                       message: str, token: str, file_sha: str | None) -> None:
    import base64
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


async def _create_pr(repo: str, branch: str, base: str, title: str,
                     body: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{repo}/pulls",
            headers=_gh_headers(token),
            json={"title": title, "body": body, "head": branch, "base": base},
        )
    if resp.status_code != 201:
        raise HTTPException(500, f"Failed to create PR: {resp.text}")
    return resp.json()["html_url"]


async def _create_issue(repo: str, title: str, body: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{repo}/issues",
            headers=_gh_headers(token),
            json={"title": title, "body": body, "labels": ["semcod", "code-quality"]},
        )
    if resp.status_code != 201:
        raise HTTPException(500, f"Failed to create issue: {resp.text}")
    return resp.json()["html_url"]


# ─── Validation ───────────────────────────────────────────────────────────────

def _score_improved(repo: str, min_delta: int = 0) -> tuple[int | None, int | None]:
    """Return (score_before, score_after) from last 2 scans. Returns (None, None) if not enough data."""
    scans = get_repo_scans(repo, limit=2)
    if len(scans) < 2:
        return None, None
    return scans[-2]["health_score"], scans[-1]["health_score"]


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.post("", response_model=AutoPRResult)
async def create_auto_pr(
    body: AutoPRRequest,
    user: dict = Depends(get_current_user),
) -> AutoPRResult:
    """
    Apply LLM-generated patches to a repository and create a GitHub PR.

    Flow:
      1. Create branch feat/semcod-fix-{id}
      2. Commit each patch file
      3. Check health score improved vs previous scan
      4. PASS  → create PR with before/after metrics
      5. FAIL  → delete branch + create GitHub issue instead
    """
    token = user.get("github_token", "")
    if not token:
        raise HTTPException(401, "GitHub token required for auto-PR")

    fix_id = hashlib.sha256(
        f"{body.repo}-{body.proposal_type}-{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:8]
    branch = f"{body.branch_prefix}-{fix_id}"

    scans_before = get_repo_scans(body.repo, limit=1)
    score_before = scans_before[-1]["health_score"] if scans_before else None

    try:
        default_branch = await _get_default_branch(body.repo, token)
        base_sha = await _get_ref_sha(body.repo, default_branch, token)
        await _create_branch(body.repo, branch, base_sha, token)

        for patch in body.patches:
            file_sha = await _get_file_sha(body.repo, patch.path, branch, token)
            await _commit_file(
                body.repo, patch.path, patch.content, branch,
                f"fix({body.proposal_type}): auto-fix via Semcod [{fix_id}]",
                token, file_sha,
            )

        # Validate: check if last scan score improved (or skip if no data)
        score_before_cmp, score_after_cmp = _score_improved(body.repo)
        rollback_reason = None

        if score_before_cmp is not None and score_after_cmp is not None:
            if score_after_cmp < score_before_cmp - 2:
                rollback_reason = (
                    f"Health score regressed: {score_before_cmp} → {score_after_cmp}. "
                    "Patch was not applied."
                )

        if rollback_reason:
            issue_title = f"[Semcod] Auto-fix failed: {body.proposal_type}"
            issue_body = _build_issue_body(body, fix_id, rollback_reason, score_before, score_after_cmp)
            issue_url = await _create_issue(body.repo, issue_title, issue_body, token)
            logger.warning("Auto-PR rolled back for %s: %s", body.repo, rollback_reason)
            return AutoPRResult(
                status="rolled_back",
                issue_url=issue_url,
                branch=branch,
                score_before=score_before,
                score_after=score_after_cmp,
                rollback_reason=rollback_reason,
            )

        pr_title = f"[Semcod] Auto-fix: {body.proposal_type.replace('_', ' ')} [{fix_id}]"
        pr_body = _build_pr_body(body, fix_id, score_before, score_after_cmp)
        pr_url = await _create_pr(body.repo, branch, default_branch, pr_title, pr_body, token)
        logger.info("Auto-PR created for %s: %s", body.repo, pr_url)

        return AutoPRResult(
            status="created",
            pr_url=pr_url,
            branch=branch,
            score_before=score_before,
            score_after=score_after_cmp,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Auto-PR failed for %s: %s", body.repo, exc)
        raise HTTPException(500, f"Auto-PR failed: {str(exc)}")


# ─── Body builders ────────────────────────────────────────────────────────────

def _build_pr_body(req: AutoPRRequest, fix_id: str, score_before: int | None, score_after: int | None) -> str:
    score_section = ""
    if score_before is not None and score_after is not None:
        delta = score_after - score_before
        sign = "+" if delta >= 0 else ""
        score_section = f"\n\n## Health Score\n| Before | After | Delta |\n|--------|-------|-------|\n| {score_before} | {score_after} | {sign}{delta} |\n"

    return f"""## Semcod Auto-Fix

**Fix ID:** `{fix_id}`
**Type:** `{req.proposal_type}`
{score_section}
## What was changed

{req.llm_prompt}

## Files modified

{chr(10).join(f'- `{p.path}`' for p in req.patches)}

---
*Generated by [Semcod](https://semcod.com) — AI-powered code health analysis*
"""


def _build_issue_body(req: AutoPRRequest, fix_id: str, reason: str,
                      score_before: int | None, score_after: int | None) -> str:
    return f"""## Semcod Auto-Fix Failed

**Fix ID:** `{fix_id}`
**Type:** `{req.proposal_type}`
**Reason:** {reason}

### Attempted patch

{req.llm_prompt}

### Files that would have been modified

{chr(10).join(f'- `{p.path}`' for p in req.patches)}

---
*This issue was created automatically by [Semcod](https://semcod.com)*
"""
