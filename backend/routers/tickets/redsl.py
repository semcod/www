"""Tickets reDSL auto-PR integration endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from db_session import get_db
from db_module.tickets_orm import (
    get_ticket,
    update_ticket,
    update_ticket_redsl_results,
    mark_ticket_error,
)
from routers.auth import get_current_user
from services.redsl_client import RedslClient

from .models import (
    RedslAutoPRRequest,
    RedslAutoPRResponse,
    _get_tenant_for_user,
)

router = APIRouter(tags=["tickets"])


@dataclass
class _RedslContext:
    """Validated ticket + auth context for reDSL processing."""
    ticket: dict
    token: str
    tenant_id: int


async def _validate_and_prepare(
    ticket_id: str, user: dict, db,
) -> _RedslContext:
    """Validate ticket ownership and GitHub token. Returns context or raises."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    tenant = _get_tenant_for_user(user, db)
    if ticket["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized")

    token = user.get("github_token", "")
    if not token:
        raise HTTPException(401, "GitHub token required for auto-PR")

    return _RedslContext(ticket=ticket, token=token, tenant_id=tenant["id"])


@dataclass
class _RedslResult:
    """Outcome of a reDSL decide/cycle run."""
    applied: list
    modified_files: list[str]
    decisions_count: int
    status: str  # "dry_run" | "analyzed" | "no_targets" | "no_changes" | "redsl_unavailable"
    error: str | None = None


async def _run_redsl(redsl: RedslClient, data: RedslAutoPRRequest) -> _RedslResult:
    """Execute reDSL decide (dry_run) or cycle (apply). Returns structured result."""
    if data.dry_run:
        decide_result = await redsl.decide(project_path=data.project_path)
        decisions = decide_result.get("decisions", []) if isinstance(decide_result, dict) else decide_result

        if not decisions:
            return _RedslResult([], [], 0, "no_targets", "No target files identified")

        applied = decisions
        modified_files = [d.get("target_path", "") for d in applied if d.get("target_path")]
        return _RedslResult(applied, modified_files, len(applied), "dry_run")

    # Real refactoring via /cycle (decide + apply in one call)
    cycle_result = await redsl.cycle(
        project_path=data.project_path,
        max_actions=data.max_actions,
        clear_history=True,
    )
    applied = cycle_result.get("decisions", [])
    modified_files = cycle_result.get("files_modified", [])
    decisions_count = cycle_result.get("decisions_count", 0) or len(modified_files)

    if cycle_result.get("proposals_applied", 0) == 0 and not modified_files:
        return _RedslResult([], [], decisions_count, "no_changes", "No refactoring changes applied")

    return _RedslResult(applied, modified_files, decisions_count, "analyzed")


def _build_redsl_response(
    ticket_id: str, result: _RedslResult, *,
    data: RedslAutoPRRequest,
    background_tasks: BackgroundTasks,
    ctx: _RedslContext,
    db,
) -> RedslAutoPRResponse:
    """Persist results, optionally queue PR creation, return API response."""
    if result.status in ("no_targets", "no_changes"):
        update_ticket(db, ticket_id, {"status": "open"})
    elif result.applied:
        update_ticket_redsl_results(db, ticket_id, result.applied, result.modified_files)

    # Queue PR creation if requested and changes were applied
    if data.auto_create_pr and not data.dry_run and result.status == "analyzed":
        background_tasks.add_task(
            _create_pr_for_ticket,
            ticket_id,
            ctx.ticket["repo"],
            ctx.ticket["provider"],
            data.project_path,
            result.applied,
            result.modified_files,
            ctx.token,
            ctx.tenant_id,
        )
        return RedslAutoPRResponse(
            status="processing",
            ticket_id=ticket_id,
            decisions_count=result.decisions_count,
            files_modified=result.modified_files,
        )

    return RedslAutoPRResponse(
        status=result.status,
        ticket_id=ticket_id,
        decisions_count=result.decisions_count,
        files_modified=result.modified_files,
        error=result.error,
    )


@router.post("/{ticket_id}/process", response_model=RedslAutoPRResponse)
async def process_ticket_with_redsl(
    ticket_id: str,
    data: RedslAutoPRRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> RedslAutoPRResponse:
    """Process ticket with reDSL engine to auto-generate PR."""
    ctx = await _validate_and_prepare(ticket_id, user, db)
    update_ticket(db, ticket_id, {"status": "analyzing"})

    try:
        redsl = RedslClient()
        if not await redsl.health():
            mark_ticket_error(db, ticket_id, "reDSL engine not available")
            return RedslAutoPRResponse(
                status="redsl_unavailable", ticket_id=ticket_id,
                decisions_count=0, files_modified=[],
                error="reDSL engine is not running",
            )

        result = await _run_redsl(redsl, data)
        return _build_redsl_response(
            ticket_id, result,
            data=data, background_tasks=background_tasks,
            ctx=ctx, db=db,
        )

    except Exception as e:
        mark_ticket_error(db, ticket_id, str(e))
        return RedslAutoPRResponse(status="error", ticket_id=ticket_id, error=str(e))


async def _create_pr_for_ticket(
    ticket_id: str,
    repo: str,
    provider: str,
    project_path: str,
    decisions: List[Dict],
    files_modified: List[str],
    token: str,
    tenant_id: int,
):
    """Background task to create PR for processed ticket."""
    from worker.tasks.autopr import create_auto_pr
    
    try:
        # Generate branch name
        branch = f"ticket-{ticket_id[:8]}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
        
        # Prepare patches from modified files
        patches = []
        for file_path in files_modified:
            full_path = f"{project_path}/{file_path}"
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                patches.append({
                    "path": file_path,
                    "content": content,
                })
            except Exception:
                continue  # Skip files that can't be read
        
        if not patches:
            mark_ticket_error(get_db().__next__(), ticket_id, "No patchable files found")
            return
        
        # Queue Celery task for PR creation
        result = create_auto_pr.delay(
            repo=repo,
            base_branch="main",  # TODO: detect default branch
            patches=patches,
            proposal_type=f"ticket-{ticket_id[:8]}",
            llm_prompt=f"Ticket: {ticket_id}",
            token=token,
            provider_type=provider,
        )
        
        # Note: Actual PR URL will be updated via webhook or polling
        # For now, mark as in_progress
        update_ticket(get_db().__next__(), ticket_id, {
            "status": "in_progress",
            "pr_branch": branch,
        })
        
    except Exception as e:
        mark_ticket_error(get_db().__next__(), ticket_id, str(e))


@router.get("/{ticket_id}/status")
async def get_ticket_processing_status(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict:
    """Get processing status for a ticket (polling endpoint)."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    
    tenant = _get_tenant_for_user(user, db)
    if ticket["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized")
    
    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "pr_url": ticket["pr_url"],
        "pr_branch": ticket["pr_branch"],
        "files_modified_count": len(ticket["files_modified"]),
        "decisions_count": len(ticket["redsl_decisions"]),
        "error_message": ticket["error_message"],
        "updated_at": ticket["updated_at"],
    }
