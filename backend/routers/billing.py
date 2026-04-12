"""Stripe billing — checkout, webhook, portal, plan status."""

import logging
from typing import Dict

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from config import (
    FRONTEND_URL,
    STRIPE_PRICE_PRO_ANNUAL,
    STRIPE_PRICE_PRO_MONTHLY,
    STRIPE_PRICE_TEAM_MONTHLY,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from database import get_subscription, upsert_subscription, increment_scan_count
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])

# ─── Plans ─────────────────────────────────────────────────────────────────────

PLANS: Dict[str, dict] = {
    "free": {
        "name": "Free",
        "scans_per_week": 3,
        "price_monthly": 0,
        "price_annual": 0,
        "stripe_price_monthly": None,
        "stripe_price_annual": None,
    },
    "pro": {
        "name": "Pro",
        "scans_per_week": -1,
        "price_monthly": 9,
        "price_annual": 81,
        "stripe_price_monthly": STRIPE_PRICE_PRO_MONTHLY,
        "stripe_price_annual": STRIPE_PRICE_PRO_ANNUAL,
    },
    "team": {
        "name": "Team",
        "scans_per_week": -1,
        "price_monthly": 29,
        "price_annual": None,
        "stripe_price_monthly": STRIPE_PRICE_TEAM_MONTHLY,
        "stripe_price_annual": None,
    },
}


def _stripe_client() -> stripe.StripeClient:
    if not STRIPE_SECRET_KEY:
        raise HTTPException(503, "Stripe not configured")
    return stripe.StripeClient(STRIPE_SECRET_KEY)


def _plan_for_price(price_id: str) -> str:
    for plan_key, plan in PLANS.items():
        if price_id in (plan.get("stripe_price_monthly"), plan.get("stripe_price_annual")):
            return plan_key
    return "free"


# ─── Pydantic models ───────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    plan: str
    billing: str = "monthly"


class BillingStatus(BaseModel):
    plan: str
    status: str
    scans_per_week: int
    scans_this_week: int
    scans_remaining: int | None


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/plans")
async def list_plans() -> Dict:
    """Return available plans and pricing (no auth required)."""
    return {
        plan_key: {
            "name": plan["name"],
            "scans_per_week": plan["scans_per_week"],
            "price_monthly": plan["price_monthly"],
            "price_annual": plan["price_annual"],
        }
        for plan_key, plan in PLANS.items()
    }


@router.get("/status", response_model=BillingStatus)
async def billing_status(user: dict = Depends(get_current_user)) -> BillingStatus:
    """Return current plan, limits, and scan usage for the authenticated user."""
    sub = get_subscription(user["id"])
    plan_key = sub["plan"] if sub else "free"
    plan = PLANS.get(plan_key, PLANS["free"])
    scans_this_week = sub["scans_this_week"] if sub else 0
    limit = plan["scans_per_week"]
    remaining = None if limit == -1 else max(0, limit - scans_this_week)

    return BillingStatus(
        plan=plan_key,
        status=sub["status"] if sub else "active",
        scans_per_week=limit,
        scans_this_week=scans_this_week,
        scans_remaining=remaining,
    )


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: dict = Depends(get_current_user),
) -> Dict:
    """
    Create a Stripe Checkout session.
    Returns { url } — frontend redirects to this URL.
    """
    plan = PLANS.get(body.plan)
    if not plan or body.plan == "free":
        raise HTTPException(400, "Invalid plan for checkout")

    price_id = (
        plan["stripe_price_annual"]
        if body.billing == "annual"
        else plan["stripe_price_monthly"]
    )
    if not price_id:
        raise HTTPException(400, f"No Stripe price configured for {body.plan}/{body.billing}")

    client = _stripe_client()

    sub = get_subscription(user["id"])
    customer_id = sub["stripe_customer_id"] if sub and sub.get("stripe_customer_id") else None

    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{FRONTEND_URL}/#tab=audit&billing=success",
        "cancel_url": f"{FRONTEND_URL}/#tab=audit&billing=cancelled",
        "metadata": {"user_id": str(user["id"]), "plan": body.plan},
    }
    if customer_id:
        params["customer"] = customer_id
    else:
        params["customer_email"] = user.get("login", "") + "@users.noreply.github.com"

    session = client.checkout.sessions.create(params=params)
    return {"url": session.url}


@router.post("/portal")
async def billing_portal(user: dict = Depends(get_current_user)) -> Dict:
    """
    Create a Stripe Customer Portal session.
    Returns { url } — lets user manage/cancel their subscription.
    """
    sub = get_subscription(user["id"])
    customer_id = sub["stripe_customer_id"] if sub else None
    if not customer_id:
        raise HTTPException(404, "No billing account found. Subscribe first.")

    client = _stripe_client()
    session = client.billing_portal.sessions.create(params={
        "customer": customer_id,
        "return_url": f"{FRONTEND_URL}/#tab=audit",
    })
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Dict:
    """
    Handle Stripe webhook events.
    Verifies signature, then processes:
      - checkout.session.completed   → activate subscription
      - customer.subscription.updated → update plan/status
      - customer.subscription.deleted → downgrade to free
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(503, "Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data)

    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(data)

    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(data)

    else:
        logger.debug("Unhandled Stripe event: %s", event_type)

    return {"received": True}


# ─── Webhook handlers ──────────────────────────────────────────────────────────

def _handle_checkout_completed(session: dict) -> None:
    user_id = int(session.get("metadata", {}).get("user_id", 0))
    plan = session.get("metadata", {}).get("plan", "pro")
    customer_id = session.get("customer", "")
    subscription_id = session.get("subscription", "")
    if not user_id:
        logger.warning("checkout.session.completed missing user_id metadata")
        return
    upsert_subscription(user_id, plan, customer_id, subscription_id, "active")
    logger.info("Subscription activated: user=%d plan=%s", user_id, plan)


def _handle_subscription_updated(subscription: dict) -> None:
    customer_id = subscription.get("customer", "")
    status = subscription.get("status", "active")
    price_id = ""
    items = subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id", "")
    plan = _plan_for_price(price_id)

    sub = _find_sub_by_customer(customer_id)
    if sub:
        upsert_subscription(sub["user_id"], plan, customer_id, subscription["id"], status)
        logger.info("Subscription updated: customer=%s plan=%s status=%s", customer_id, plan, status)


def _handle_subscription_deleted(subscription: dict) -> None:
    customer_id = subscription.get("customer", "")
    sub = _find_sub_by_customer(customer_id)
    if sub:
        upsert_subscription(sub["user_id"], "free", customer_id, "", "cancelled")
        logger.info("Subscription cancelled: customer=%s → free", customer_id)


def _find_sub_by_customer(customer_id: str) -> dict | None:
    """Lookup subscription row by stripe_customer_id."""
    from db_session import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM subscriptions WHERE stripe_customer_id = :cid"),
            {"cid": customer_id}
        ).mappings().fetchone()
    return dict(row) if row else None


# ─── Scan gate (used by audit router) ─────────────────────────────────────────

def check_scan_allowed(user_id: int) -> None:
    """
    Raise HTTP 402 if the user has hit their weekly scan limit.
    Call this before starting a new audit.
    """
    sub = get_subscription(user_id)
    plan_key = sub["plan"] if sub else "free"
    plan = PLANS.get(plan_key, PLANS["free"])
    limit = plan["scans_per_week"]
    if limit == -1:
        return
    scans_this_week = sub["scans_this_week"] if sub else 0
    if scans_this_week >= limit:
        raise HTTPException(
            402,
            {
                "error": "scan_limit_reached",
                "plan": plan_key,
                "scans_per_week": limit,
                "scans_this_week": scans_this_week,
                "upgrade_url": f"{FRONTEND_URL}/#billing=upgrade",
            },
        )
    increment_scan_count(user_id)
