"""User and subscription database operations using SQLAlchemy ORM."""
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session

from db_models import User, Subscription


def upsert_user(
    db: Session,
    github_id: int,
    login: str,
    name: str,
    avatar_url: str,
    github_token: str,
) -> Dict:
    """Create or update a user. Returns the user dict."""
    user = db.query(User).filter(User.github_id == github_id).first()
    
    if user:
        # Update existing
        user.login = login
        user.name = name
        user.avatar_url = avatar_url
        user.github_token = github_token
    else:
        # Create new
        user = User(
            github_id=github_id,
            login=login,
            name=name,
            avatar_url=avatar_url,
            github_token=github_token,
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "github_id": user.github_id,
        "login": user.login,
        "name": user.name,
        "avatar_url": user.avatar_url,
    }


def get_user_by_github_id(db: Session, github_id: int) -> Optional[Dict]:
    """Get user by GitHub ID."""
    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        return None
    return {
        "id": user.id,
        "github_id": user.github_id,
        "login": user.login,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "github_token": user.github_token,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def get_user_by_id(db: Session, user_id: int) -> Optional[Dict]:
    """Get user by internal ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return {
        "id": user.id,
        "github_id": user.github_id,
        "login": user.login,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "github_token": user.github_token,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def get_subscription(db: Session, user_id: int) -> Optional[Dict]:
    """Get active subscription for a user. Returns None if not found (treat as free)."""
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .order_by(Subscription.id.desc())
        .first()
    )
    if not subscription:
        return None
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan": subscription.plan,
        "stripe_customer_id": subscription.stripe_customer_id,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "status": subscription.status,
        "scans_this_week": subscription.scans_this_week,
        "week_reset_at": subscription.week_reset_at,
        "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
        "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None,
    }


def upsert_subscription(
    db: Session,
    user_id: int,
    plan: str,
    stripe_customer_id: str = "",
    stripe_subscription_id: str = "",
    status: str = "active",
) -> Dict:
    """Create or update subscription for a user."""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    now = datetime.now(timezone.utc).isoformat()
    
    if subscription:
        # Update existing
        subscription.plan = plan
        subscription.stripe_customer_id = stripe_customer_id
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.status = status
        subscription.updated_at = datetime.now(timezone.utc)
    else:
        # Create new
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status=status,
            week_reset_at=now,
        )
        db.add(subscription)
    
    db.commit()
    return get_subscription(db, user_id)


def increment_scan_count(db: Session, user_id: int) -> int:
    """Increment scans_this_week counter. Resets if a new week has started. Returns new count."""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    
    if not subscription:
        # Create new subscription with scan count
        subscription = Subscription(
            user_id=user_id,
            plan="free",
            scans_this_week=1,
            week_reset_at=now_iso,
        )
        db.add(subscription)
        db.commit()
        return 1
    
    week_reset_at = subscription.week_reset_at
    scans = subscription.scans_this_week or 0
    
    # Check if week has passed
    if week_reset_at:
        try:
            reset_dt = datetime.fromisoformat(week_reset_at.replace("Z", "+00:00"))
            if (now - reset_dt).days >= 7:
                scans = 0
                week_reset_at = now_iso
        except ValueError:
            week_reset_at = now_iso
            scans = 0
    else:
        week_reset_at = now_iso
    
    new_count = scans + 1
    subscription.scans_this_week = new_count
    subscription.week_reset_at = week_reset_at
    subscription.updated_at = now
    
    db.commit()
    return new_count
