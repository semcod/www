"""Marketplace billing endpoints - billing status and plans."""

from typing import Any, Dict
from datetime import datetime
from fastapi import APIRouter, Depends

from routers.auth import get_current_user
from services.billing import get_usage_tracker, BillingEventType

router = APIRouter(tags=["marketplace"])


@router.get("/billing/status")
async def get_billing_status(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current billing status and usage."""
    from database import get_or_create_tenant

    provider_user_id = str(
        user.get("github_id")
        or user.get("gitlab_id")
        or user.get("gitea_id")
        or user.get("id")
    )
    tenant = get_or_create_tenant(
        provider=user.get("provider", "github"),
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
    )

    usage_tracker = get_usage_tracker()
    now = datetime.now()
    report = usage_tracker.get_usage_report(tenant["id"], now.year, now.month)

    plan = tenant.get("plan", "free")
    limits = usage_tracker._get_plan_limits(plan)

    return {
        "plan": plan,
        "limits": limits,
        "current_month": {
            "analysis_used": usage_tracker._get_current_month_usage(
                tenant["id"], BillingEventType.PR_ANALYSIS
            ),
            "autofix_used": usage_tracker._get_current_month_usage(
                tenant["id"], BillingEventType.AUTOFIX_RUN
            ),
        },
        "usage_report": report,
    }


@router.get("/billing/plans")
async def list_billing_plans() -> Dict[str, Any]:
    """List available billing plans."""
    from config import FREE_TIER_LIMITS, PRO_TIER_LIMITS, TEAM_TIER_LIMITS

    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "limits": FREE_TIER_LIMITS,
                "features": ["10 PR analyses/month", "1 repo", "No auto-fix"],
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 29,
                "limits": PRO_TIER_LIMITS,
                "features": [
                    "1,000 PR analyses/month",
                    "10 repos",
                    "50 auto-fix/month",
                ],
            },
            {
                "id": "team",
                "name": "Team",
                "price": 99,
                "limits": TEAM_TIER_LIMITS,
                "features": ["Unlimited", "Unlimited repos", "Unlimited auto-fix"],
            },
        ],
        "usage_pricing": {
            "analysis_per_pr": {"cents": 50, "usd": 0.50},
            "autofix_per_run": {"cents": 100, "usd": 1.00},
        },
    }
