"""Session-aware wrapper functions for backward compatibility."""
from db_session import SessionLocal
from .scans_orm import (
    save_scan as save_scan_orm,
    get_recent_scans as get_recent_scans_orm,
    get_repo_scans as get_repo_scans_orm,
    get_total_scan_count as get_total_scan_count_orm,
    save_audit_result as save_audit_result_orm,
    get_audit_result as get_audit_result_orm,
    save_badge_cache as save_badge_cache_orm,
    get_badge_cache as get_badge_cache_orm,
)
from .users_orm import (
    upsert_user as upsert_user_orm,
    get_user_by_github_id as get_user_by_github_id_orm,
    get_user_by_id as get_user_by_id_orm,
    get_subscription as get_subscription_orm,
    upsert_subscription as upsert_subscription_orm,
    increment_scan_count as increment_scan_count_orm,
)
from .tenants_orm import (
    get_or_create_tenant as get_or_create_tenant_orm,
    get_tenant_by_id as get_tenant_by_id_orm,
    update_tenant_plan as update_tenant_plan_orm,
)
from .repositories_orm import (
    get_or_create_repository as get_or_create_repository_orm,
    get_tenant_repositories as get_tenant_repositories_orm,
    get_repository_by_full_name as get_repository_by_full_name_orm,
)
from .installations_orm import (
    create_installation as create_installation_orm,
    get_installation as get_installation_orm,
    get_tenant_installations as get_tenant_installations_orm,
    delete_installation as delete_installation_orm,
    update_installation_scan as update_installation_scan_orm,
)
from .events_orm import (
    queue_event as queue_event_orm,
    get_pending_events as get_pending_events_orm,
    update_event_status as update_event_status_orm,
)


# Scan operations
def save_scan(scan_data):
    db = SessionLocal()
    try:
        return save_scan_orm(db, scan_data)
    finally:
        db.close()


def get_recent_scans(limit=100):
    db = SessionLocal()
    try:
        return get_recent_scans_orm(db, limit)
    finally:
        db.close()


def get_repo_scans(repo, limit=100):
    db = SessionLocal()
    try:
        return get_repo_scans_orm(db, repo, limit)
    finally:
        db.close()


def get_total_scan_count():
    db = SessionLocal()
    try:
        return get_total_scan_count_orm(db)
    finally:
        db.close()


def save_audit_result(audit_id, audit_data):
    db = SessionLocal()
    try:
        return save_audit_result_orm(db, audit_id, audit_data)
    finally:
        db.close()


def get_audit_result(audit_id):
    db = SessionLocal()
    try:
        return get_audit_result_orm(db, audit_id)
    finally:
        db.close()


def save_badge_cache(repo, badge_data):
    db = SessionLocal()
    try:
        return save_badge_cache_orm(db, repo, badge_data)
    finally:
        db.close()


def get_badge_cache(repo):
    db = SessionLocal()
    try:
        return get_badge_cache_orm(db, repo)
    finally:
        db.close()


# User operations
def upsert_user(github_id, login, name, avatar_url, github_token):
    db = SessionLocal()
    try:
        return upsert_user_orm(db, github_id, login, name, avatar_url, github_token)
    finally:
        db.close()


def get_user_by_github_id(github_id):
    db = SessionLocal()
    try:
        return get_user_by_github_id_orm(db, github_id)
    finally:
        db.close()


def get_user_by_id(user_id):
    db = SessionLocal()
    try:
        return get_user_by_id_orm(db, user_id)
    finally:
        db.close()


def get_subscription(user_id):
    db = SessionLocal()
    try:
        return get_subscription_orm(db, user_id)
    finally:
        db.close()


def upsert_subscription(user_id, plan, stripe_customer_id="", stripe_subscription_id="", status="active"):
    db = SessionLocal()
    try:
        return upsert_subscription_orm(db, user_id, plan, stripe_customer_id, stripe_subscription_id, status)
    finally:
        db.close()


def increment_scan_count(user_id):
    db = SessionLocal()
    try:
        return increment_scan_count_orm(db, user_id)
    finally:
        db.close()


# Tenant operations
def get_or_create_tenant(provider, provider_user_id, login, name="", email="", avatar_url=""):
    db = SessionLocal()
    try:
        return get_or_create_tenant_orm(db, provider, provider_user_id, login, name, email, avatar_url)
    finally:
        db.close()


def get_tenant_by_id(tenant_id):
    db = SessionLocal()
    try:
        return get_tenant_by_id_orm(db, tenant_id)
    finally:
        db.close()


def update_tenant_plan(tenant_id, plan, billing_customer_id="", billing_subscription_id=""):
    db = SessionLocal()
    try:
        return update_tenant_plan_orm(db, tenant_id, plan, billing_customer_id, billing_subscription_id)
    finally:
        db.close()


# Repository operations
def get_or_create_repository(tenant_id, provider, repo_provider_id, name, full_name, description="", private=False, default_branch="main", web_url="", clone_url=""):
    db = SessionLocal()
    try:
        return get_or_create_repository_orm(db, tenant_id, provider, repo_provider_id, name, full_name, description, private, default_branch, web_url, clone_url)
    finally:
        db.close()


def get_tenant_repositories(tenant_id):
    db = SessionLocal()
    try:
        return get_tenant_repositories_orm(db, tenant_id)
    finally:
        db.close()


def get_repository_by_full_name(tenant_id, provider, full_name):
    db = SessionLocal()
    try:
        return get_repository_by_full_name_orm(db, tenant_id, provider, full_name)
    finally:
        db.close()


# Installation operations
def create_installation(tenant_id, repository_id, apps, webhook_id="", webhook_secret=""):
    db = SessionLocal()
    try:
        return create_installation_orm(db, tenant_id, repository_id, apps, webhook_id, webhook_secret)
    finally:
        db.close()


def get_installation(tenant_id, repository_id):
    db = SessionLocal()
    try:
        return get_installation_orm(db, tenant_id, repository_id)
    finally:
        db.close()


def get_tenant_installations(tenant_id):
    db = SessionLocal()
    try:
        return get_tenant_installations_orm(db, tenant_id)
    finally:
        db.close()


def delete_installation(tenant_id, repository_id):
    db = SessionLocal()
    try:
        return delete_installation_orm(db, tenant_id, repository_id)
    finally:
        db.close()


def update_installation_scan(tenant_id, repository_id, score):
    db = SessionLocal()
    try:
        return update_installation_scan_orm(db, tenant_id, repository_id, score)
    finally:
        db.close()


# Event operations
def queue_event(event_id, event_type, provider, repo_full_name, pr_id, payload):
    db = SessionLocal()
    try:
        return queue_event_orm(db, event_id, event_type, provider, repo_full_name, pr_id, payload)
    finally:
        db.close()


def get_pending_events(limit=100):
    db = SessionLocal()
    try:
        return get_pending_events_orm(db, limit)
    finally:
        db.close()


def update_event_status(event_id, status, error_message=""):
    db = SessionLocal()
    try:
        return update_event_status_orm(db, event_id, status, error_message)
    finally:
        db.close()
