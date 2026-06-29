"""Tickets ORM — CRUD for ticket-driven auto-PR generation.

Query/stats functions moved to db_module.tickets_query — re-exported here
for backward compatibility.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db_models import Ticket


def generate_ticket_id() -> str:
    """Generate unique ticket ID."""
    timestamp = datetime.now(timezone.utc).isoformat()
    return hashlib.sha256(timestamp.encode()).hexdigest()[:12]


def create_ticket(db: Session, tenant_id: int, payload: Dict) -> Dict:
    """Create new ticket for auto-PR generation."""
    ticket = Ticket(
        ticket_id=payload.get("ticket_id") or generate_ticket_id(),
        tenant_id=tenant_id,
        repo=payload["repo"],
        provider=payload.get("provider", "github"),
        title=payload["title"],
        description=payload.get("description", ""),
        ticket_type=payload["ticket_type"],  # 'feature' or 'bugfix'
        status=payload.get("status", "open"),
        priority=payload.get("priority", "medium"),
        pr_url=payload.get("pr_url", ""),
        pr_branch=payload.get("pr_branch", ""),
        pr_number=payload.get("pr_number"),
        redsl_decisions=json.dumps(payload.get("redsl_decisions", [])),
        files_modified=json.dumps(payload.get("files_modified", [])),
        error_message=payload.get("error_message", ""),
        resolved_at=None,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return _ticket_to_dict(ticket)


def get_ticket(db: Session, ticket_id: str) -> Optional[Dict]:
    """Get single ticket by ID."""
    row = db.execute(
        select(Ticket).where(Ticket.ticket_id == ticket_id)
    ).scalar_one_or_none()
    return _ticket_to_dict(row) if row else None


def get_ticket_by_pr(db: Session, pr_number: int, repo: str) -> Optional[Dict]:
    """Get ticket associated with a PR."""
    row = db.execute(
        select(Ticket).where(Ticket.pr_number == pr_number, Ticket.repo == repo)
    ).scalar_one_or_none()
    return _ticket_to_dict(row) if row else None


def update_ticket(db: Session, ticket_id: str, updates: Dict) -> Optional[Dict]:
    """Update ticket fields."""
    row = db.execute(
        select(Ticket).where(Ticket.ticket_id == ticket_id)
    ).scalar_one_or_none()
    if not row:
        return None

    for k, v in updates.items():
        if hasattr(row, k) and v is not None:
            # Handle JSON fields
            if k in ("redsl_decisions", "files_modified") and isinstance(v, list):
                setattr(row, k, json.dumps(v))
            else:
                setattr(row, k, v)

    row.updated_at = datetime.now(timezone.utc)

    # If status is merged or closed, set resolved_at
    if updates.get("status") in ("merged", "closed") and not row.resolved_at:
        row.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _ticket_to_dict(row)


def delete_ticket(db: Session, ticket_id: str) -> bool:
    """Delete ticket (soft delete by marking as closed)."""
    row = db.execute(
        select(Ticket).where(Ticket.ticket_id == ticket_id)
    ).scalar_one_or_none()
    if not row:
        return False
    row.status = "closed"
    row.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return True


def _ticket_to_dict(t: Ticket) -> Dict:
    """Convert Ticket ORM to dict."""
    return {
        "id": t.id,
        "ticket_id": t.ticket_id,
        "tenant_id": t.tenant_id,
        "repo": t.repo,
        "provider": t.provider,
        "title": t.title,
        "description": t.description,
        "ticket_type": t.ticket_type,
        "status": t.status,
        "priority": t.priority,
        "pr_url": t.pr_url,
        "pr_branch": t.pr_branch,
        "pr_number": t.pr_number,
        "redsl_decisions": json.loads(t.redsl_decisions or "[]"),
        "files_modified": json.loads(t.files_modified or "[]"),
        "error_message": t.error_message,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
    }


def update_ticket_pr_info(
    db: Session, ticket_id: str, pr_url: str, pr_branch: str, pr_number: int
) -> Optional[Dict]:
    """Update ticket with PR information after auto-generation."""
    return update_ticket(
        db,
        ticket_id,
        {
            "pr_url": pr_url,
            "pr_branch": pr_branch,
            "pr_number": pr_number,
            "status": "pr_created",
        },
    )


def update_ticket_redsl_results(
    db: Session, ticket_id: str, decisions: List[Dict], files: List[str]
) -> Optional[Dict]:
    """Update ticket with reDSL analysis results."""
    return update_ticket(
        db,
        ticket_id,
        {
            "redsl_decisions": decisions,
            "files_modified": files,
            "status": "in_progress",
        },
    )


def mark_ticket_error(db: Session, ticket_id: str, error: str) -> Optional[Dict]:
    """Mark ticket as failed with error message."""
    return update_ticket(db, ticket_id, {"status": "error", "error_message": error})


# ─── Re-exports from tickets_query for backward compatibility ────────────

from db_module.tickets_query import (  # noqa: E402, F401
    get_tickets_by_tenant,
    get_tickets_by_repo,
    count_tickets_by_status,
    get_tickets_requiring_action,
    get_ticket_stats,
    search_tickets,
    get_tickets_with_pr_status,
    bulk_update_ticket_status,
    get_tickets_by_date_range,
    get_priority_distribution,
    get_average_resolution_time,
    clone_ticket,
    archive_old_tickets,
    get_tickets_for_redsl_processing,
    link_ticket_to_audit,
)
