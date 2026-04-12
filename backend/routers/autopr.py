"""Auto-PR generation — applies LLM-generated patches and creates GitHub PRs."""

import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.scan_service import get_repo_scans
from services.autopr_helpers import (
    BranchManager,
    PatchApplier,
    PRCreator,
    generate_fix_id,
)
from services.redsl_client import RedslClient
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/autopr", tags=["autopr"])


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


class RedslRefactorRequest(BaseModel):
    repo: str
    project_path: str
    proposal_type: str = "redsl_refactor"
    max_actions: int = 10
    dry_run: bool = False
    branch_prefix: str = "semcod-fix"


class RedslRefactorResult(BaseModel):
    status: str
    redsl_available: bool
    decisions_count: int = 0
    pr_url: str | None = None
    branch: str | None = None
    error: str | None = None




# ─── Validation ───────────────────────────────────────────────────────────────

def _score_improved(repo: str, min_delta: int = 0) -> tuple[int | None, int | None]:
    """Return (score_before, score_after) from last 2 scans. Returns (None, None) if not enough data."""
    scans = get_repo_scans(repo, limit=2)
    if len(scans) < 2:
        return None, None
    return scans[-2]["health_score"], scans[-1]["health_score"]


# ─── Endpoint ─────────────────────────────────────────────────────────────────

async def _prepare_branch(repo: str, branch: str, token: str) -> str:
    """Create a new branch from the default branch. Returns default branch name."""
    default_branch = await BranchManager.get_default_branch(repo, token)
    base_sha = await BranchManager.get_ref_sha(repo, default_branch, token)
    await BranchManager.create_branch(repo, branch, base_sha, token)
    return default_branch


async def _commit_patches(repo: str, patches: list, branch: str, proposal_type: str, fix_id: str, token: str) -> None:
    """Commit each patch file to the branch."""
    for patch in patches:
        file_sha = await PatchApplier.get_file_sha(repo, patch.path, branch, token)
        await PatchApplier.commit_file(
            repo, patch.path, patch.content, branch,
            f"fix({proposal_type}): auto-fix via Semcod [{fix_id}]",
            token, file_sha,
        )


def _check_rollback(repo: str) -> str | None:
    """Check if health score regressed. Returns rollback reason or None."""
    score_before, score_after = _score_improved(repo)
    if score_before is not None and score_after is not None:
        if score_after < score_before - 2:
            return f"Health score regressed: {score_before} → {score_after}. Patch was not applied."
    return None


async def _handle_rollback(repo: str, proposal_type: str, fix_id: str, llm_prompt: str,
                           patches: list, token: str, score_before: int | None,
                           score_after: int | None, rollback_reason: str, branch: str) -> AutoPRResult:
    """Create a GitHub issue for the failed auto-fix."""
    issue_title = f"[Semcod] Auto-fix failed: {proposal_type}"
    issue_body = PRCreator.build_issue_body(proposal_type, fix_id, rollback_reason, llm_prompt, patches, score_before, score_after)
    issue_url = await PRCreator.create_issue(repo, issue_title, issue_body, token)
    logger.warning("Auto-PR rolled back for %s: %s", repo, rollback_reason)
    return AutoPRResult(status="rolled_back", issue_url=issue_url, branch=branch,
                        score_before=score_before, score_after=score_after, rollback_reason=rollback_reason)


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

    fix_id = generate_fix_id(body.repo, body.proposal_type)
    branch = f"{body.branch_prefix}-{fix_id}"

    scans_before = get_repo_scans(body.repo, limit=1)
    score_before = scans_before[-1]["health_score"] if scans_before else None

    try:
        default_branch = await _prepare_branch(body.repo, branch, token)
        await _commit_patches(body.repo, body.patches, branch, body.proposal_type, fix_id, token)

        rollback_reason = _check_rollback(body.repo)
        if rollback_reason:
            _, score_after_cmp = _score_improved(body.repo)
            return await _handle_rollback(body.repo, body.proposal_type, fix_id, body.llm_prompt,
                                         body.patches, token, score_before, score_after_cmp, rollback_reason, branch)

        _, score_after_cmp = _score_improved(body.repo)
        pr_title = f"[Semcod] Auto-fix: {body.proposal_type.replace('_', ' ')} [{fix_id}]"
        pr_body = PRCreator.build_pr_body(body.proposal_type, fix_id, body.llm_prompt, body.patches, score_before, score_after_cmp)
        pr_url = await PRCreator.create_pr(body.repo, branch, default_branch, pr_title, pr_body, token)
        logger.info("Auto-PR created for %s: %s", body.repo, pr_url)

        return AutoPRResult(status="created", pr_url=pr_url, branch=branch,
                            score_before=score_before, score_after=score_after_cmp)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Auto-PR failed for %s: %s", body.repo, exc)
        raise HTTPException(500, f"Auto-PR failed: {str(exc)}")


# ─── reDSL-powered endpoint ───────────────────────────────────────────────────

async def _run_redsl_refactor(redsl: RedslClient, project_path: str, max_actions: int, dry_run: bool) -> list:
    """Run reDSL refactor and return decisions list."""
    refactor_result = await redsl.refactor(
        project_path=project_path,
        max_actions=max_actions,
        dry_run=dry_run,
        fmt="json",
    )
    return refactor_result.get("decisions", [])


async def _commit_redsl_decisions(repo: str, decisions: list, project_path: str,
                                  branch: str, proposal_type: str, fix_id: str, token: str) -> set[str]:
    """Commit each decision's target file to the branch. Returns set of committed file paths."""
    committed_files: set[str] = set()
    for decision in decisions:
        target_file = decision.get("target_file", "")
        if not target_file or target_file in committed_files:
            continue

        file_path = Path(project_path) / target_file
        if not file_path.exists():
            continue

        content = file_path.read_text(encoding="utf-8", errors="replace")
        file_sha = await PatchApplier.get_file_sha(repo, target_file, branch, token)
        await PatchApplier.commit_file(
            repo, target_file, content, branch,
            f"refactor({proposal_type}): {decision.get('action', 'auto-fix')} via reDSL [{fix_id}]",
            token, file_sha,
        )
        committed_files.add(target_file)
    return committed_files


@router.post("/redsl", response_model=RedslRefactorResult)
async def create_redsl_auto_pr(
    body: RedslRefactorRequest,
    user: dict = Depends(get_current_user),
) -> RedslRefactorResult:
    """
    Use reDSL engine to analyze and refactor a project, then create a PR.

    Flow:
      1. Check reDSL engine availability
      2. Run reDSL refactor (dry_run=False) on the project
      3. Collect decisions and transformed files
      4. Create branch, commit changes, create PR
    """
    token = user.get("github_token", "")
    if not token:
        raise HTTPException(401, "GitHub token required for auto-PR")

    redsl = RedslClient()
    available = await redsl.health()

    if not available:
        return RedslRefactorResult(
            status="redsl_unavailable",
            redsl_available=False,
            error="reDSL engine is not running. Start it with: docker-compose up agent",
        )

    try:
        decisions = await _run_redsl_refactor(redsl, body.project_path, body.max_actions, body.dry_run)
        if not decisions:
            return RedslRefactorResult(status="no_decisions", redsl_available=True, decisions_count=0)

        fix_id = generate_fix_id(body.repo, body.proposal_type)
        branch = f"{body.branch_prefix}-{fix_id}"

        default_branch = await _prepare_branch(body.repo, branch, token)
        committed_files = await _commit_redsl_decisions(
            body.repo, decisions, body.project_path, branch, body.proposal_type, fix_id, token)

        if not committed_files:
            return RedslRefactorResult(status="no_changes", redsl_available=True, decisions_count=len(decisions))

        pr_title = f"[Semcod] reDSL refactor: {body.proposal_type.replace('_', ' ')} [{fix_id}]"
        pr_body = _build_redsl_pr_body(body.proposal_type, fix_id, decisions, committed_files)
        pr_url = await PRCreator.create_pr(body.repo, branch, default_branch, pr_title, pr_body, token)
        logger.info("reDSL Auto-PR created for %s: %s", body.repo, pr_url)

        return RedslRefactorResult(status="created", redsl_available=True,
                                   decisions_count=len(decisions), pr_url=pr_url, branch=branch)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("reDSL Auto-PR failed for %s: %s", body.repo, exc)
        return RedslRefactorResult(status="failed", redsl_available=True, error=str(exc))


def _build_redsl_pr_body(proposal_type: str, fix_id: str, decisions: list, files: set) -> str:
    """Build PR body from reDSL decisions."""
    decision_lines = []
    for d in decisions:
        action = d.get("action", "unknown")
        target = d.get("target_file", "")
        score = d.get("score", 0)
        decision_lines.append(f"| `{action}` | `{target}` | {score:.1f} |")

    return f"""## Semcod reDSL Auto-Fix

**Fix ID:** `{fix_id}`
**Type:** `{proposal_type}`
**Engine:** reDSL

## Refactoring decisions ({len(decisions)} applied)

| Action | Target | Score |
|--------|--------|-------|
{chr(10).join(decision_lines)}

## Files modified ({len(files)})

{chr(10).join(f'- `{f}`' for f in sorted(files))}

---
*Generated by [Semcod](https://semcod.com) — AI-powered code health analysis with [reDSL](https://github.com/softrebel/redsl)*
"""


