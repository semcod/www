"""Event queue database operations using SQLAlchemy ORM."""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from db_models import Event


def queue_event(
    db: Session,
    event_id: str,
    event_type: str,
    provider: str,
    repo_full_name: str,
    pr_id: Optional[int],
    payload: Dict,
) -> int:
    """Queue a new event for processing."""
    event = Event(
        event_id=event_id,
        type=event_type,
        provider=provider,
        repo_full_name=repo_full_name,
        pr_id=pr_id,
        payload=json.dumps(payload),
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event.id


def get_pending_events(db: Session, limit: int = 100) -> List[Dict]:
    """Get pending events for processing."""
    events = (
        db.query(Event)
        .filter(Event.status == "pending")
        .order_by(Event.created_at.asc())
        .limit(limit)
        .all()
    )

    results = []
    for event in events:
        results.append(
            {
                "id": event.id,
                "event_id": event.event_id,
                "type": event.type,
                "provider": event.provider,
                "repo_full_name": event.repo_full_name,
                "pr_id": event.pr_id,
                "payload": json.loads(event.payload) if event.payload else {},
                "status": event.status,
                "retry_count": event.retry_count,
                "error_message": event.error_message,
                "processed_at": event.processed_at.isoformat()
                if event.processed_at
                else None,
                "created_at": event.created_at.isoformat()
                if event.created_at
                else None,
            }
        )

    return results


def update_event_status(
    db: Session, event_id: int, status: str, error_message: str = ""
) -> None:
    """Update event processing status."""
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return

    event.status = status
    event.error_message = error_message

    if status == "completed":
        event.processed_at = datetime.now(timezone.utc)
        event.error_message = ""
    elif status == "failed":
        event.retry_count = (event.retry_count or 0) + 1
    else:
        event.error_message = ""

    db.commit()
