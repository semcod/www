"""Installation database operations using SQLAlchemy ORM."""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from db_models import Installation, Repository


def create_installation(
    db: Session,
    tenant_id: int,
    repository_id: int,
    apps: List[str],
    webhook_id: str = "",
    webhook_secret: str = "",
) -> Dict:
    """Create app installation for a repository."""
    installation = (
        db.query(Installation)
        .filter(
            Installation.tenant_id == tenant_id,
            Installation.repository_id == repository_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if installation:
        # Update existing
        installation.apps = json.dumps(apps)
        installation.webhook_id = webhook_id
        installation.webhook_secret = webhook_secret
        installation.updated_at = now
        installation.status = "active"
    else:
        # Create new
        installation = Installation(
            tenant_id=tenant_id,
            repository_id=repository_id,
            apps=json.dumps(apps),
            webhook_id=webhook_id,
            webhook_secret=webhook_secret,
            installed_at=now,
            updated_at=now,
            status="active",
        )
        db.add(installation)

    db.commit()
    db.refresh(installation)
    return get_installation(db, tenant_id, repository_id) or {}


def get_installation(db: Session, tenant_id: int, repository_id: int) -> Optional[Dict]:
    """Get installation by tenant and repository."""
    installation = (
        db.query(Installation, Repository)
        .join(Repository, Installation.repository_id == Repository.id)
        .filter(
            Installation.tenant_id == tenant_id,
            Installation.repository_id == repository_id,
        )
        .first()
    )

    if not installation:
        return None

    inst, repo = installation

    result = {
        "id": inst.id,
        "tenant_id": inst.tenant_id,
        "repository_id": inst.repository_id,
        "apps": json.loads(inst.apps) if inst.apps else [],
        "webhook_id": inst.webhook_id,
        "webhook_secret": inst.webhook_secret,
        "webhook_url": inst.webhook_url,
        "status": inst.status,
        "installed_at": inst.installed_at.isoformat() if inst.installed_at else None,
        "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
        "last_scan_at": inst.last_scan_at.isoformat() if inst.last_scan_at else None,
        "last_scan_score": inst.last_scan_score,
        "repo_full_name": repo.full_name,
        "repo_provider": repo.provider,
    }

    return result


def get_tenant_installations(db: Session, tenant_id: int) -> List[Dict]:
    """Get all installations for a tenant."""
    installations = (
        db.query(Installation, Repository)
        .join(Repository, Installation.repository_id == Repository.id)
        .filter(Installation.tenant_id == tenant_id)
        .all()
    )

    results = []
    for inst, repo in installations:
        result = {
            "id": inst.id,
            "tenant_id": inst.tenant_id,
            "repository_id": inst.repository_id,
            "apps": json.loads(inst.apps) if inst.apps else [],
            "webhook_id": inst.webhook_id,
            "webhook_secret": inst.webhook_secret,
            "webhook_url": inst.webhook_url,
            "status": inst.status,
            "installed_at": inst.installed_at.isoformat()
            if inst.installed_at
            else None,
            "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
            "last_scan_at": inst.last_scan_at.isoformat()
            if inst.last_scan_at
            else None,
            "last_scan_score": inst.last_scan_score,
            "repo_full_name": repo.full_name,
            "repo_provider": repo.provider,
        }

        results.append(result)

    return results


def delete_installation(db: Session, tenant_id: int, repository_id: int) -> bool:
    """Delete installation (soft delete - set inactive)."""
    installation = (
        db.query(Installation)
        .filter(
            Installation.tenant_id == tenant_id,
            Installation.repository_id == repository_id,
        )
        .first()
    )

    if not installation:
        return False

    installation.status = "inactive"
    installation.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True


def update_installation_scan(
    db: Session, tenant_id: int, repository_id: int, score: int
) -> None:
    """Update last scan info for installation."""
    installation = (
        db.query(Installation)
        .filter(
            Installation.tenant_id == tenant_id,
            Installation.repository_id == repository_id,
        )
        .first()
    )

    if installation:
        now = datetime.now(timezone.utc)
        installation.last_scan_at = now
        installation.last_scan_score = score
        installation.updated_at = now
        db.commit()
