"""Tickets query builders — search, filter, stats, and bulk operations.

Extracted from tickets_orm.py to reduce fan-out and keep CRUD focused.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.orm import Session

from db_models import Ticket
from db_module.tickets_orm import _ticket_to_dict


# ─── Listing & filtering ────────────────────────────────────────────────────


def get_tickets_by_tenant(
    db: Session, tenant_id: int, status: Optional[str] = None
) -> List[Dict]:
    """List all tickets for a tenant, optionally filtered by status."""
    query = select(Ticket).where(Ticket.tenant_id == tenant_id)
    if status:
        query = query.where(Ticket.status == status)
    query = query.order_by(desc(Ticket.created_at))
    rows = db.execute(query).scalars().all()
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_by_repo(db: Session, tenant_id: int, repo: str) -> List[Dict]:
    """Get all tickets for a specific repository."""
    rows = (
        db.execute(
            select(Ticket)
            .where(Ticket.tenant_id == tenant_id, Ticket.repo == repo)
            .order_by(desc(Ticket.created_at))
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_requiring_action(db: Session, tenant_id: int) -> List[Dict]:
    """Get tickets that need auto-PR generation (open status)."""
    rows = (
        db.execute(
            select(Ticket)
            .where(
                Ticket.tenant_id == tenant_id, Ticket.status.in_(["open", "analyzing"])
            )
            .order_by(desc(Ticket.priority), desc(Ticket.created_at))
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_with_pr_status(db: Session, tenant_id: int) -> List[Dict]:
    """Get tickets that have PRs created, for PR status monitoring."""
    rows = (
        db.execute(
            select(Ticket)
            .where(
                Ticket.tenant_id == tenant_id,
                Ticket.status.in_(["pr_created", "merged"]),
                Ticket.pr_number.isnot(None),
            )
            .order_by(desc(Ticket.updated_at))
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_for_redsl_processing(db: Session, batch_size: int = 10) -> List[Dict]:
    """Get tickets ready for reDSL auto-processing (open status)."""
    rows = (
        db.execute(
            select(Ticket)
            .where(Ticket.status == "open")
            .order_by(desc(Ticket.priority), desc(Ticket.created_at))
            .limit(batch_size)
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


def get_tickets_by_date_range(
    db: Session, tenant_id: int, start_date: datetime, end_date: datetime
) -> List[Dict]:
    """Get tickets created within date range."""
    rows = (
        db.execute(
            select(Ticket)
            .where(
                Ticket.tenant_id == tenant_id,
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date,
            )
            .order_by(desc(Ticket.created_at))
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


def search_tickets(db: Session, tenant_id: int, query: str) -> List[Dict]:
    """Search tickets by title or description."""
    search_pattern = f"%{query}%"
    rows = (
        db.execute(
            select(Ticket)
            .where(
                Ticket.tenant_id == tenant_id,
                or_(
                    Ticket.title.ilike(search_pattern),
                    Ticket.description.ilike(search_pattern),
                ),
            )
            .order_by(desc(Ticket.created_at))
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(r) for r in rows]


# ─── Statistics ──────────────────────────────────────────────────────────────


def count_tickets_by_status(db: Session, tenant_id: int) -> Dict[str, int]:
    """Get ticket counts grouped by status."""
    result = db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .where(Ticket.tenant_id == tenant_id)
        .group_by(Ticket.status)
    ).all()
    return {status: count for status, count in result}


def get_ticket_stats(db: Session, tenant_id: int) -> Dict:
    """Get comprehensive ticket statistics for tenant."""
    total = (
        db.execute(
            select(func.count(Ticket.id)).where(Ticket.tenant_id == tenant_id)
        ).scalar()
        or 0
    )

    open_count = (
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.tenant_id == tenant_id, Ticket.status.in_(["open", "analyzing"])
            )
        ).scalar()
        or 0
    )

    in_progress = (
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.tenant_id == tenant_id, Ticket.status == "in_progress"
            )
        ).scalar()
        or 0
    )

    pr_created = (
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.tenant_id == tenant_id, Ticket.status == "pr_created"
            )
        ).scalar()
        or 0
    )

    merged = (
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.tenant_id == tenant_id, Ticket.status == "merged"
            )
        ).scalar()
        or 0
    )

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
        "success_rate": round(merged / (merged + pr_created) * 100, 1)
        if (merged + pr_created) > 0
        else 0,
    }


def get_priority_distribution(db: Session, tenant_id: int) -> Dict[str, int]:
    """Get ticket distribution by priority."""
    result = db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .where(Ticket.tenant_id == tenant_id)
        .group_by(Ticket.priority)
    ).all()
    return {p: c for p, c in result}


def get_average_resolution_time(db: Session, tenant_id: int) -> Optional[float]:
    """Calculate average time from creation to resolution (in hours)."""
    result = db.execute(
        select(
            func.avg(
                func.julianday(Ticket.resolved_at) - func.julianday(Ticket.created_at)
            )
            * 24
        ).where(Ticket.tenant_id == tenant_id, Ticket.resolved_at.isnot(None))
    ).scalar()
    return round(result, 2) if result else None


# ─── Bulk & utility ──────────────────────────────────────────────────────────


def bulk_update_ticket_status(
    db: Session, ticket_ids: List[str], new_status: str
) -> int:
    """Bulk update status for multiple tickets."""
    result = db.execute(
        update(Ticket)
        .where(Ticket.ticket_id.in_(ticket_ids))
        .values(status=new_status, updated_at=datetime.now(timezone.utc))
    )
    db.commit()
    return result.rowcount


def clone_ticket(
    db: Session,
    tenant_id: int,
    original_ticket_id: str,
    new_title: Optional[str] = None,
) -> Optional[Dict]:
    """Clone an existing ticket (for similar feature requests)."""
    from db_module.tickets_orm import get_ticket, create_ticket

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
    cutoff_date = datetime.now(timezone.utc) - __import__("datetime").timedelta(
        days=days
    )

    result = (
        db.execute(
            select(Ticket).where(
                Ticket.tenant_id == tenant_id,
                Ticket.status.in_(["closed", "merged"]),
                Ticket.updated_at < cutoff_date,
            )
        )
        .scalars()
        .all()
    )

    count = 0
    for ticket in result:
        ticket.status = "archived"
        count += 1

    db.commit()
    return count


def link_ticket_to_audit(db: Session, ticket_id: str, audit_id: str) -> Optional[Dict]:
    """Link ticket to an audit run (for tracking analysis)."""
    ticket = db.execute(
        select(Ticket).where(Ticket.ticket_id == ticket_id)
    ).scalar_one_or_none()
    if not ticket:
        return None

    current_desc = ticket.description or ""
    if f"Audit: {audit_id}" not in current_desc:
        ticket.description = f"{current_desc}\n\nAudit: {audit_id}".strip()
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)

    return _ticket_to_dict(ticket)
