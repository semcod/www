"""Tickets ORM — CRUD for ticket-driven auto-PR generation."""
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, desc
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


def get_tickets_by_tenant(db: Session, tenant_id: int, status: Optional[str] = None) -> List[Dict]:
    """List all tickets for a tenant, optionally filtered by status."""
    query = select(Ticket).where(Ticket.tenant_id == tenant_id)
    if status:
        query = query.where(Ticket.status == status)
    query = query.order_by(desc(Ticket.created_at))
    rows = db.execute(query).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def get_ticket(db: Session, ticket_id: str) -> Optional[Dict]:
    """Get single ticket by ID."""
    row = db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id)).scalar_one_or_none()
    return _ticket_to_dict(row) if row else None


def get_ticket_by_pr(db: Session, pr_number: int, repo: str) -> Optional[Dict]:
    """Get ticket associated with a PR."""
    row = db.execute(
        select(Ticket).where(
            Ticket.pr_number == pr_number,
            Ticket.repo == repo
        )
    ).scalar_one_or_none()
    return _ticket_to_dict(row) if row else None


def update_ticket(db: Session, ticket_id: str, updates: Dict) -> Optional[Dict]:
    """Update ticket fields."""
    row = db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id)).scalar_one_or_none()
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
    row = db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id)).scalar_one_or_none()
    if not row:
        return False
    row.status = "closed"
    row.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return True


def get_tickets_by_repo(db: Session, tenant_id: int, repo: str) -> List[Dict]:
    """Get all tickets for a specific repository."""
    rows = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            Ticket.repo == repo
        ).order_by(desc(Ticket.created_at))
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


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


def count_tickets_by_status(db: Session, tenant_id: int) -> Dict[str, int]:
    """Get ticket counts grouped by status."""
    from sqlalchemy import func
    result = db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .where(Ticket.tenant_id == tenant_id)
        .group_by(Ticket.status)
    ).all()
    return {status: count for status, count in result}


def get_tickets_requiring_action(db: Session, tenant_id: int) -> List[Dict]:
    """Get tickets that need auto-PR generation (open status)."""
    rows = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_(["open", "analyzing"])
        ).order_by(desc(Ticket.priority), desc(Ticket.created_at))
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def update_ticket_pr_info(db: Session, ticket_id: str, pr_url: str, pr_branch: str, pr_number: int) -> Optional[Dict]:
    """Update ticket with PR information after auto-generation."""
    return update_ticket(db, ticket_id, {
        "pr_url": pr_url,
        "pr_branch": pr_branch,
        "pr_number": pr_number,
        "status": "pr_created"
    })


def update_ticket_redsl_results(db: Session, ticket_id: str, decisions: List[Dict], files: List[str]) -> Optional[Dict]:
    """Update ticket with reDSL analysis results."""
    return update_ticket(db, ticket_id, {
        "redsl_decisions": decisions,
        "files_modified": files,
        "status": "in_progress"
    })


def mark_ticket_error(db: Session, ticket_id: str, error: str) -> Optional[Dict]:
    """Mark ticket as failed with error message."""
    return update_ticket(db, ticket_id, {
        "status": "error",
        "error_message": error
    })


def get_ticket_stats(db: Session, tenant_id: int) -> Dict:
    """Get comprehensive ticket statistics for tenant."""
    from sqlalchemy import func
    
    total = db.execute(
        select(func.count(Ticket.id)).where(Ticket.tenant_id == tenant_id)
    ).scalar() or 0
    
    open_count = db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_(["open", "analyzing"])
        )
    ).scalar() or 0
    
    in_progress = db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status == "in_progress"
        )
    ).scalar() or 0
    
    pr_created = db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status == "pr_created"
        )
    ).scalar() or 0
    
    merged = db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status == "merged"
        )
    ).scalar() or 0
    
    by_type = db.execute(
        select(Ticket.ticket_type, func.count(Ticket.id))
        .where(Ticket.tenant_id == tenant_id)
        .group_by(Ticket.ticket_type)
    ).all()
    
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "pr_created": pr_created,
        "merged": merged,
        "by_type": {t: c for t, c in by_type},
        "success_rate": round(merged / (merged + pr_created) * 100, 1) if (merged + pr_created) > 0 else 0
    }


def search_tickets(db: Session, tenant_id: int, query: str) -> List[Dict]:
    """Search tickets by title or description."""
    from sqlalchemy import or_
    search_pattern = f"%{query}%"
    rows = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            or_(
                Ticket.title.ilike(search_pattern),
                Ticket.description.ilike(search_pattern)
            )
        ).order_by(desc(Ticket.created_at))
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_with_pr_status(db: Session, tenant_id: int) -> List[Dict]:
    """Get tickets that have PRs created, for PR status monitoring."""
    rows = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_(["pr_created", "merged"]),
            Ticket.pr_number.isnot(None)
        ).order_by(desc(Ticket.updated_at))
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def bulk_update_ticket_status(db: Session, ticket_ids: List[str], new_status: str) -> int:
    """Bulk update status for multiple tickets."""
    from sqlalchemy import update
    result = db.execute(
        update(Ticket)
        .where(Ticket.ticket_id.in_(ticket_ids))
        .values(status=new_status, updated_at=datetime.now(timezone.utc))
    )
    db.commit()
    return result.rowcount


def get_tickets_by_date_range(db: Session, tenant_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Get tickets created within date range."""
    rows = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            Ticket.created_at >= start_date,
            Ticket.created_at <= end_date
        ).order_by(desc(Ticket.created_at))
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def get_priority_distribution(db: Session, tenant_id: int) -> Dict[str, int]:
    """Get ticket distribution by priority."""
    from sqlalchemy import func
    result = db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .where(Ticket.tenant_id == tenant_id)
        .group_by(Ticket.priority)
    ).all()
    return {p: c for p, c in result}


def get_average_resolution_time(db: Session, tenant_id: int) -> Optional[float]:
    """Calculate average time from creation to resolution (in hours)."""
    from sqlalchemy import func
    result = db.execute(
        select(
            func.avg(
                func.julianday(Ticket.resolved_at) - func.julianday(Ticket.created_at)
            ) * 24
        ).where(
            Ticket.tenant_id == tenant_id,
            Ticket.resolved_at.isnot(None)
        )
    ).scalar()
    return round(result, 2) if result else None


def clone_ticket(db: Session, tenant_id: int, original_ticket_id: str, new_title: Optional[str] = None) -> Optional[Dict]:
    """Clone an existing ticket (for similar feature requests)."""
    original = get_ticket(db, original_ticket_id)
    if not original:
        return None
    
    new_payload = {
        "title": new_title or f"[Clone] {original['title']}",
        "repo": original["repo"],
        "provider": original["provider"],
        "description": original["description"],
        "ticket_type": original["ticket_type"],
        "priority": original["priority"],
    }
    
    return create_ticket(db, tenant_id, new_payload)


def archive_old_tickets(db: Session, tenant_id: int, days: int = 90) -> int:
    """Archive (soft delete) tickets older than specified days."""
    from sqlalchemy import func
    cutoff_date = datetime.now(timezone.utc) - __import__('datetime').timedelta(days=days)
    
    result = db.execute(
        select(Ticket).where(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_(["closed", "merged"]),
            Ticket.updated_at < cutoff_date
        )
    ).scalars().all()
    
    count = 0
    for ticket in result:
        ticket.status = "archived"
        count += 1
    
    db.commit()
    return count


def get_tickets_for_redsl_processing(db: Session, batch_size: int = 10) -> List[Dict]:
    """Get tickets ready for reDSL auto-processing (open status)."""
    rows = db.execute(
        select(Ticket).where(
            Ticket.status == "open"
        ).order_by(desc(Ticket.priority), desc(Ticket.created_at))
        .limit(batch_size)
    ).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def link_ticket_to_audit(db: Session, ticket_id: str, audit_id: str) -> Optional[Dict]:
    """Link ticket to an audit run (for tracking analysis)."""
    # Store in description or metadata
    ticket = db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id)).scalar_one_or_none()
    if not ticket:
        return None
    
    current_desc = ticket.description or ""
    if f"Audit: {audit_id}" not in current_desc:
        ticket.description = f"{current_desc}\n\nAudit: {audit_id}".strip()
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
    
    return _ticket_to_dict(ticket)
