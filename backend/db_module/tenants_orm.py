"""Tenant database operations using SQLAlchemy ORM."""
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session

from db_models import Tenant


def get_or_create_tenant(
    db: Session,
    provider: str,
    provider_user_id: str,
    login: str,
    name: str = "",
    email: str = "",
    avatar_url: str = "",
) -> Dict:
    """Get existing tenant or create new one."""
    tenant = (
        db.query(Tenant)
        .filter(
            Tenant.provider == provider,
            Tenant.provider_user_id == provider_user_id,
        )
        .first()
    )
    
    if tenant:
        return {
            "id": tenant.id,
            "provider": tenant.provider,
            "provider_user_id": tenant.provider_user_id,
            "login": tenant.login,
            "name": tenant.name,
            "email": tenant.email,
            "avatar_url": tenant.avatar_url,
            "plan": tenant.plan,
            "billing_customer_id": tenant.billing_customer_id,
            "billing_subscription_id": tenant.billing_subscription_id,
            "usage_limits": tenant.usage_limits,
            "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
            "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None,
            "is_new": False,
        }
    
    # Create new tenant
    now = datetime.now(timezone.utc)
    tenant = Tenant(
        provider=provider,
        provider_user_id=provider_user_id,
        login=login,
        name=name,
        email=email,
        avatar_url=avatar_url,
        created_at=now,
        updated_at=now,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return {
        "id": tenant.id,
        "provider": tenant.provider,
        "provider_user_id": tenant.provider_user_id,
        "login": tenant.login,
        "name": tenant.name,
        "email": tenant.email,
        "avatar_url": tenant.avatar_url,
        "plan": tenant.plan,
        "billing_customer_id": tenant.billing_customer_id,
        "billing_subscription_id": tenant.billing_subscription_id,
        "usage_limits": tenant.usage_limits,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None,
        "is_new": True,
    }


def get_tenant_by_id(db: Session, tenant_id: int) -> Optional[Dict]:
    """Get tenant by ID."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        return None
    return {
        "id": tenant.id,
        "provider": tenant.provider,
        "provider_user_id": tenant.provider_user_id,
        "login": tenant.login,
        "name": tenant.name,
        "email": tenant.email,
        "avatar_url": tenant.avatar_url,
        "plan": tenant.plan,
        "billing_customer_id": tenant.billing_customer_id,
        "billing_subscription_id": tenant.billing_subscription_id,
        "usage_limits": tenant.usage_limits,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None,
    }


def update_tenant_plan(
    db: Session,
    tenant_id: int,
    plan: str,
    billing_customer_id: str = "",
    billing_subscription_id: str = "",
) -> Optional[Dict]:
    """Update tenant's billing plan."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        return None
    
    tenant.plan = plan
    tenant.billing_customer_id = billing_customer_id
    tenant.billing_subscription_id = billing_subscription_id
    tenant.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    return get_tenant_by_id(db, tenant_id)
