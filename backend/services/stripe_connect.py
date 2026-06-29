"""Stripe Connect — revenue share payouts to marketplace publishers."""

import logging
from typing import Dict, Optional

import stripe

from config import STRIPE_SECRET_KEY, FRONTEND_URL

logger = logging.getLogger(__name__)

REVENUE_SHARE_RATE = 0.70  # 70% to publisher


def _stripe() -> None:
    stripe.api_key = STRIPE_SECRET_KEY


def create_connect_account(email: str, country: str = "US") -> Dict:
    """Create a Stripe Express Connect account for a publisher."""
    _stripe()
    account = stripe.Account.create(
        type="express",
        country=country,
        email=email,
        capabilities={"transfers": {"requested": True}},
    )
    logger.info("Created Connect account %s for %s", account.id, email)
    return {"account_id": account.id, "status": account.payouts_enabled}


def create_onboarding_link(account_id: str) -> str:
    """Return onboarding URL for publisher to complete KYC."""
    _stripe()
    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=f"{FRONTEND_URL}/settings?connect=refresh",
        return_url=f"{FRONTEND_URL}/settings?connect=success",
        type="account_onboarding",
    )
    return link.url


def get_account_status(account_id: str) -> Dict:
    """Return payouts_enabled, charges_enabled, requirements."""
    _stripe()
    account = stripe.Account.retrieve(account_id)
    return {
        "account_id": account_id,
        "payouts_enabled": account.payouts_enabled,
        "charges_enabled": account.charges_enabled,
        "requirements": account.requirements.get("currently_due", []),
    }


def transfer_revenue(
    amount_cents: int, account_id: str, metadata: Optional[Dict] = None
) -> Dict:
    """Transfer publisher share (70%) to their Connect account."""
    _stripe()
    share = int(amount_cents * REVENUE_SHARE_RATE)
    if share < 50:
        raise ValueError(f"Transfer amount {share}¢ below Stripe minimum (50¢)")

    transfer = stripe.Transfer.create(
        amount=share,
        currency="usd",
        destination=account_id,
        metadata=metadata or {},
    )
    logger.info("Transferred %d¢ to %s (transfer %s)", share, account_id, transfer.id)
    return {
        "transfer_id": transfer.id,
        "amount_cents": share,
        "destination": account_id,
        "status": "succeeded",
    }
