"""Repository database operations using SQLAlchemy ORM."""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from db_models import Repository


def get_or_create_repository(
    db: Session,
    tenant_id: int,
    provider: str,
    repo_provider_id: str,
    name: str,
    full_name: str,
    description: str = "",
    private: bool = False,
    default_branch: str = "main",
    web_url: str = "",
    clone_url: str = "",
) -> Dict:
    """Get existing repository or create new one for tenant."""
    repo = (
        db.query(Repository)
        .filter(
            Repository.tenant_id == tenant_id,
            Repository.provider == provider,
            Repository.full_name == full_name,
        )
        .first()
    )
    
    if repo:
        return {
            "id": repo.id,
            "tenant_id": repo.tenant_id,
            "provider": repo.provider,
            "repo_provider_id": repo.repo_provider_id,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": bool(repo.private),
            "default_branch": repo.default_branch,
            "web_url": repo.web_url,
            "clone_url": repo.clone_url,
            "status": repo.status,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "is_new": False,
        }
    
    # Create new repository
    now = datetime.now(timezone.utc)
    repo = Repository(
        tenant_id=tenant_id,
        provider=provider,
        repo_provider_id=repo_provider_id,
        name=name,
        full_name=full_name,
        description=description,
        private=1 if private else 0,
        default_branch=default_branch,
        web_url=web_url,
        clone_url=clone_url,
        created_at=now,
        updated_at=now,
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    
    return {
        "id": repo.id,
        "tenant_id": repo.tenant_id,
        "provider": repo.provider,
        "repo_provider_id": repo.repo_provider_id,
        "name": repo.name,
        "full_name": repo.full_name,
        "description": repo.description,
        "private": bool(repo.private),
        "default_branch": repo.default_branch,
        "web_url": repo.web_url,
        "clone_url": repo.clone_url,
        "status": repo.status,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
        "is_new": True,
    }


def get_tenant_repositories(db: Session, tenant_id: int) -> List[Dict]:
    """Get all repositories for a tenant."""
    repos = (
        db.query(Repository)
        .filter(Repository.tenant_id == tenant_id)
        .order_by(Repository.updated_at.desc())
        .all()
    )
    
    return [
        {
            "id": repo.id,
            "tenant_id": repo.tenant_id,
            "provider": repo.provider,
            "repo_provider_id": repo.repo_provider_id,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": bool(repo.private),
            "default_branch": repo.default_branch,
            "web_url": repo.web_url,
            "clone_url": repo.clone_url,
            "status": repo.status,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
        }
        for repo in repos
    ]


def get_repository_by_full_name(
    db: Session, tenant_id: int, provider: str, full_name: str
) -> Optional[Dict]:
    """Get repository by tenant + provider + full_name."""
    repo = (
        db.query(Repository)
        .filter(
            Repository.tenant_id == tenant_id,
            Repository.provider == provider,
            Repository.full_name == full_name,
        )
        .first()
    )
    
    if not repo:
        return None
    
    return {
        "id": repo.id,
        "tenant_id": repo.tenant_id,
        "provider": repo.provider,
        "repo_provider_id": repo.repo_provider_id,
        "name": repo.name,
        "full_name": repo.full_name,
        "description": repo.description,
        "private": bool(repo.private),
        "default_branch": repo.default_branch,
        "web_url": repo.web_url,
        "clone_url": repo.clone_url,
        "status": repo.status,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
    }
