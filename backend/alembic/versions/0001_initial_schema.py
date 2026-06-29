"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "scans" in existing:
        return  # Tables already created by init_db() — stamp only

    op.create_table(
        "scans",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("repo", sa.String, nullable=False),
        sa.Column("health_score", sa.Integer, nullable=True),
        sa.Column("grade", sa.String(4), nullable=True),
        sa.Column("stats", sa.Text, nullable=True),
        sa.Column("completed", sa.String, nullable=True),
        sa.Column("sandbox", sa.Integer, server_default="0"),
        sa.Column("badge_url", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("idx_scans_repo", "scans", ["repo"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("github_id", sa.Integer, unique=True, nullable=False),
        sa.Column("login", sa.String, nullable=False),
        sa.Column("name", sa.String, server_default=""),
        sa.Column("avatar_url", sa.Text, server_default=""),
        sa.Column("github_token", sa.Text, server_default=""),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("plan", sa.String, nullable=False, server_default="free"),
        sa.Column("stripe_customer_id", sa.String, server_default=""),
        sa.Column("stripe_subscription_id", sa.String, server_default=""),
        sa.Column("status", sa.String, nullable=False, server_default="active"),
        sa.Column("scans_this_week", sa.Integer, server_default="0"),
        sa.Column("week_reset_at", sa.String, server_default=""),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("idx_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("provider_user_id", sa.String, nullable=False),
        sa.Column("login", sa.String, nullable=False),
        sa.Column("name", sa.String, server_default=""),
        sa.Column("email", sa.String, server_default=""),
        sa.Column("avatar_url", sa.Text, server_default=""),
        sa.Column("plan", sa.String, server_default="free"),
        sa.Column("billing_customer_id", sa.String, server_default=""),
        sa.Column("billing_subscription_id", sa.String, server_default=""),
        sa.Column("usage_limits", sa.Text, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "provider", "provider_user_id", name="uq_tenants_provider_user"
        ),
    )

    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, nullable=False),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("repo_provider_id", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("private", sa.Integer, server_default="0"),
        sa.Column("default_branch", sa.String, server_default="main"),
        sa.Column("web_url", sa.Text, server_default=""),
        sa.Column("clone_url", sa.Text, server_default=""),
        sa.Column("status", sa.String, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("idx_repositories_tenant_id", "repositories", ["tenant_id"])

    op.create_table(
        "installations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer, nullable=False),
        sa.Column("repository_id", sa.Integer, nullable=False),
        sa.Column("apps", sa.Text, server_default="[]"),
        sa.Column("webhook_id", sa.String, server_default=""),
        sa.Column("webhook_secret", sa.String, server_default=""),
        sa.Column("webhook_url", sa.Text, server_default=""),
        sa.Column("status", sa.String, server_default="active"),
        sa.Column(
            "installed_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("last_scan_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scan_score", sa.Integer, nullable=True),
    )
    op.create_index("idx_installations_tenant_id", "installations", ["tenant_id"])
    op.create_index(
        "idx_installations_repository_id", "installations", ["repository_id"]
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.String, unique=True, nullable=False),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("repo_full_name", sa.String, nullable=False),
        sa.Column("pr_id", sa.Integer, nullable=True),
        sa.Column("payload", sa.Text, nullable=False),
        sa.Column("status", sa.String, server_default="pending"),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        sa.Column("error_message", sa.Text, server_default=""),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("idx_events_status", "events", ["status"])
    op.create_index("idx_events_type", "events", ["type"])
    op.create_index("idx_events_provider", "events", ["provider"])

    op.create_table(
        "audit_results",
        sa.Column("audit_id", sa.String, primary_key=True),
        sa.Column("repo", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("started", sa.String, nullable=True),
        sa.Column("completed", sa.String, nullable=True),
        sa.Column("health_score", sa.Integer, nullable=True),
        sa.Column("grade", sa.String, nullable=True),
        sa.Column("stats", sa.Text, nullable=True),
        sa.Column("metrics", sa.Text, nullable=True),
        sa.Column("recommendations", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("idx_audit_results_repo", "audit_results", ["repo"])
    op.create_index("idx_audit_results_status", "audit_results", ["status"])

    op.create_table(
        "badge_cache",
        sa.Column("repo", sa.String, primary_key=True),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("grade", sa.String, nullable=True),
        sa.Column("updated", sa.String, nullable=True),
        sa.Column("weekly_issues", sa.Integer, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("badge_cache")
    op.drop_table("audit_results")
    op.drop_table("events")
    op.drop_table("installations")
    op.drop_table("repositories")
    op.drop_table("tenants")
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.drop_table("scans")
