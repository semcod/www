"""SQLAlchemy ORM models — declarative base for all database tables."""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Index, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase


def _utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo = Column(String, nullable=False, index=True)
    health_score = Column(Integer)
    grade = Column(String(4))
    stats = Column(Text)
    completed = Column(String)
    sandbox = Column(Integer, default=0)
    badge_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan = Column(String, nullable=False, default="free")
    stripe_customer_id = Column(String, default="")
    stripe_subscription_id = Column(String, default="")
    status = Column(String, nullable=False, default="active")
    scans_this_week = Column(Integer, default=0)
    week_reset_at = Column(String, default="")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(Integer, unique=True, nullable=False)
    login = Column(String, nullable=False)
    name = Column(String, default="")
    avatar_url = Column(Text, default="")
    github_token = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)
    login = Column(String, nullable=False)
    name = Column(String, default="")
    email = Column(String, default="")
    avatar_url = Column(Text, default="")
    plan = Column(String, default="free")
    billing_customer_id = Column(String, default="")
    billing_subscription_id = Column(String, default="")
    usage_limits = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    provider = Column(String, nullable=False)
    repo_provider_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    description = Column(Text, default="")
    private = Column(Integer, default=0)
    default_branch = Column(String, default="main")
    web_url = Column(Text, default="")
    clone_url = Column(Text, default="")
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Installation(Base):
    __tablename__ = "installations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    repository_id = Column(Integer, nullable=False, index=True)
    apps = Column(Text, default="[]")
    webhook_id = Column(String, default="")
    webhook_secret = Column(String, default="")
    webhook_url = Column(Text, default="")
    status = Column(String, default="active")
    installed_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    last_scan_score = Column(Integer, nullable=True)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_status", "status"),
        Index("idx_events_type", "type"),
        Index("idx_events_provider", "provider"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    repo_full_name = Column(String, nullable=False)
    pr_id = Column(Integer, nullable=True)
    payload = Column(Text, nullable=False)
    status = Column(String, default="pending")
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, default="")
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class AuditResult(Base):
    __tablename__ = "audit_results"
    __table_args__ = (
        Index("idx_audit_results_repo", "repo"),
        Index("idx_audit_results_status", "status"),
    )

    audit_id = Column(String, primary_key=True)
    repo = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started = Column(String)
    completed = Column(String)
    health_score = Column(Integer)
    grade = Column(String)
    stats = Column(Text)
    metrics = Column(Text)
    recommendations = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class BadgeCache(Base):
    __tablename__ = "badge_cache"

    repo = Column(String, primary_key=True)
    score = Column(Integer)
    grade = Column(String)
    updated = Column(String)
    weekly_issues = Column(Integer, default=0)
