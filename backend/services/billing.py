"""Usage-based billing service with Stripe integration."""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from config import (
    STRIPE_SECRET_KEY,
    STRIPE_PRICE_ANALYSIS_PER_PR,
    STRIPE_PRICE_AUTOFIX_PER_RUN,
    FREE_TIER_LIMITS,
    PRO_TIER_LIMITS,
    TEAM_TIER_LIMITS,
)


class BillingEventType(Enum):
    PR_ANALYSIS = "pr_analysis"
    AUTOFIX_RUN = "autofix_run"
    REPO_ACTIVE = "repo_active"


class UsageTracker:
    """Tracks usage per tenant for billing purposes."""

    def __init__(self, db_connection=None):
        self.db = db_connection

    def record_usage(
        self,
        tenant_id: int,
        event_type: BillingEventType,
        quantity: int = 1,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Record usage event for billing.

        Returns:
            Dict with usage info and cost
        """
        from db_module.wrappers import get_tenant_by_id

        tenant = get_tenant_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        plan = tenant.get("plan", "free")
        limits = self._get_plan_limits(plan)

        # Check current usage
        current_usage = self._get_current_month_usage(tenant_id, event_type)
        new_usage = current_usage + quantity

        # Check if within limits
        limit_key = self._event_type_to_limit_key(event_type)
        plan_limit = limits.get(limit_key, 0)
        within_limit = new_usage <= plan_limit or plan_limit == float("inf")

        # Calculate cost (only if over limit or on usage-based plan)
        cost_cents = 0
        if not within_limit:
            overage = new_usage - plan_limit
            cost_cents = self._calculate_cost(event_type, overage)

        # Store usage record
        self._store_usage_record(tenant_id, event_type, quantity, metadata, cost_cents)

        return {
            "tenant_id": tenant_id,
            "event_type": event_type.value,
            "quantity": quantity,
            "current_month_total": new_usage,
            "plan_limit": plan_limit,
            "within_limit": within_limit,
            "cost_cents": cost_cents,
            "plan": plan,
        }

    def check_can_execute(
        self,
        tenant_id: int,
        event_type: BillingEventType,
        quantity: int = 1,
    ) -> Tuple[bool, str]:
        """Check if tenant can execute action based on billing limits.

        Returns:
            (can_execute: bool, reason: str)
        """
        from db_module.wrappers import get_tenant_by_id

        tenant = get_tenant_by_id(tenant_id)
        if not tenant:
            return False, "Tenant not found"

        plan = tenant.get("plan", "free")

        # Free tier checks
        if plan == "free":
            if event_type == BillingEventType.AUTOFIX_RUN:
                return False, "Auto-fix requires Pro plan or higher"

        # Check limits
        limits = self._get_plan_limits(plan)
        current_usage = self._get_current_month_usage(tenant_id, event_type)
        limit_key = self._event_type_to_limit_key(event_type)
        plan_limit = limits.get(limit_key, 0)

        if current_usage + quantity > plan_limit and plan_limit != float("inf"):
            if plan == "free":
                return (
                    False,
                    f"Free tier limit reached ({plan_limit}/month). Upgrade to Pro.",
                )
            # Over limit but allowed (will be billed)
            return (
                True,
                f"Over limit - will be billed ${self._calculate_cost(event_type, quantity) / 100:.2f}",
            )

        return True, "OK"

    def get_usage_report(self, tenant_id: int, year: int, month: int) -> Dict[str, Any]:
        """Get detailed usage report for a month."""
        from db_session import engine
        from sqlalchemy import text

        month_str = f"{year}-{month:02d}"
        with engine.connect() as conn:
            # strftime works in SQLite; TO_CHAR/date_trunc works in PG
            # Use LIKE for cross-DB compat
            rows = conn.execute(
                text(
                    "SELECT event_type, SUM(quantity), SUM(cost_cents) "
                    "FROM usage_records "
                    "WHERE tenant_id = :tid AND CAST(created_at AS TEXT) LIKE :month "
                    "GROUP BY event_type"
                ),
                {"tid": tenant_id, "month": f"{month_str}%"},
            ).fetchall()

        usage_by_type = {
            row[0]: {
                "quantity": row[1],
                "cost_cents": row[2],
                "cost_usd": row[2] / 100 if row[2] else 0,
            }
            for row in rows
        }

        total_cost = sum(u["cost_cents"] for u in usage_by_type.values())

        return {
            "tenant_id": tenant_id,
            "year": year,
            "month": month,
            "usage_by_type": usage_by_type,
            "total_cost_cents": total_cost,
            "total_cost_usd": total_cost / 100,
        }

    def _get_plan_limits(self, plan: str) -> Dict[str, Any]:
        """Get limits for a plan."""
        limits_map = {
            "free": FREE_TIER_LIMITS,
            "pro": PRO_TIER_LIMITS,
            "team": TEAM_TIER_LIMITS,
        }
        return limits_map.get(plan, FREE_TIER_LIMITS)

    def _get_current_month_usage(
        self,
        tenant_id: int,
        event_type: BillingEventType,
    ) -> int:
        """Get current month's usage for an event type."""
        from db_session import engine
        from sqlalchemy import text

        now = datetime.now(timezone.utc)
        month_prefix = now.strftime("%Y-%m")
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COALESCE(SUM(quantity), 0) "
                    "FROM usage_records "
                    "WHERE tenant_id = :tid AND event_type = :etype "
                    "AND CAST(created_at AS TEXT) LIKE :month"
                ),
                {
                    "tid": tenant_id,
                    "etype": event_type.value,
                    "month": f"{month_prefix}%",
                },
            ).fetchone()

        return result[0] if result else 0

    def _store_usage_record(
        self,
        tenant_id: int,
        event_type: BillingEventType,
        quantity: int,
        metadata: Dict[str, Any],
        cost_cents: int,
    ):
        """Store usage record in database."""
        from db_session import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            # Create table if not exists (cross-DB)
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS usage_records ("
                    "id SERIAL PRIMARY KEY, "
                    "tenant_id INTEGER NOT NULL, "
                    "event_type TEXT NOT NULL, "
                    "quantity INTEGER DEFAULT 1, "
                    "cost_cents INTEGER DEFAULT 0, "
                    "metadata TEXT DEFAULT '{}', "
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                )
            )

            conn.execute(
                text(
                    "INSERT INTO usage_records (tenant_id, event_type, quantity, cost_cents, metadata) "
                    "VALUES (:tid, :etype, :qty, :cost, :meta)"
                ),
                {
                    "tid": tenant_id,
                    "etype": event_type.value,
                    "qty": quantity,
                    "cost": cost_cents,
                    "meta": json.dumps(metadata or {}),
                },
            )
            conn.commit()

    def _calculate_cost(self, event_type: BillingEventType, quantity: int) -> int:
        """Calculate cost in cents for usage."""
        price_map = {
            BillingEventType.PR_ANALYSIS: STRIPE_PRICE_ANALYSIS_PER_PR,
            BillingEventType.AUTOFIX_RUN: STRIPE_PRICE_AUTOFIX_PER_RUN,
            BillingEventType.REPO_ACTIVE: STRIPE_PRICE_REPO_ACTIVE_MONTHLY,
        }
        price_per_unit = price_map.get(event_type, 0)
        return price_per_unit * quantity

    def _event_type_to_limit_key(self, event_type: BillingEventType) -> str:
        """Map event type to limit key."""
        mapping = {
            BillingEventType.PR_ANALYSIS: "analysis_per_month",
            BillingEventType.AUTOFIX_RUN: "autofix_per_month",
            BillingEventType.REPO_ACTIVE: "repos_active",
        }
        return mapping.get(event_type, "analysis_per_month")


class StripeBilling:
    """Stripe integration for usage-based billing."""

    def __init__(self):
        self.stripe = None
        if STRIPE_SECRET_KEY:
            import stripe

            stripe.api_key = STRIPE_SECRET_KEY
            self.stripe = stripe

    def create_customer(self, tenant_id: int, email: str, name: str) -> Optional[str]:
        """Create Stripe customer for tenant."""
        if not self.stripe:
            return None

        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata={"tenant_id": tenant_id},
            )
            return customer.id
        except Exception as e:
            print(f"[billing] Failed to create customer: {e}")
            return None

    def create_subscription(self, customer_id: str, price_id: str) -> Optional[str]:
        """Create subscription for customer."""
        if not self.stripe:
            return None

        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={"billing_type": "usage_based"},
            )
            return subscription.id
        except Exception as e:
            print(f"[billing] Failed to create subscription: {e}")
            return None

    def record_usage(self, subscription_item_id: str, quantity: int) -> bool:
        """Record usage to Stripe for metered billing."""
        if not self.stripe:
            return False

        try:
            self.stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=int(datetime.now(timezone.utc).timestamp()),
            )
            return True
        except Exception as e:
            print(f"[billing] Failed to record usage: {e}")
            return False

    def get_invoice_preview(self, customer_id: str) -> Dict[str, Any]:
        """Get upcoming invoice preview."""
        if not self.stripe:
            return {"error": "Stripe not configured"}

        try:
            invoice = self.stripe.Invoice.upcoming(customer=customer_id)
            return {
                "amount_due": invoice.amount_due,
                "amount_due_usd": invoice.amount_due / 100,
                "currency": invoice.currency,
                "lines": [
                    {
                        "description": line.description,
                        "amount": line.amount,
                    }
                    for line in invoice.lines.data
                ],
            }
        except Exception as e:
            return {"error": str(e)}


# Global instances
_usage_tracker: Optional[UsageTracker] = None
_stripe_billing: Optional[StripeBilling] = None


def get_usage_tracker() -> UsageTracker:
    """Get singleton usage tracker."""
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker()
    return _usage_tracker


def get_stripe_billing() -> StripeBilling:
    """Get singleton Stripe billing."""
    global _stripe_billing
    if _stripe_billing is None:
        _stripe_billing = StripeBilling()
    return _stripe_billing
