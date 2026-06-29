"""Marketplace Connect endpoints — Stripe Connect revenue share for publishers."""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from routers.auth import get_current_user

router = APIRouter(prefix="/api/marketplace/connect", tags=["marketplace"])


class ConnectRegisterRequest(BaseModel):
    country: str = "US"


class PayoutRequest(BaseModel):
    amount_cents: int
    publisher_account_id: str
    description: Optional[str] = None


@router.post("/register")
async def register_publisher(
    request: ConnectRegisterRequest,
    user: dict = Depends(get_current_user),
) -> Dict:
    """Create a Stripe Express Connect account for this publisher."""
    from services.stripe_connect import create_connect_account, create_onboarding_link

    email = user.get("email") or f"{user.get('login', 'publisher')}@semcod.dev"
    try:
        result = create_connect_account(email=email, country=request.country)
        onboarding_url = create_onboarding_link(result["account_id"])
        return {
            "account_id": result["account_id"],
            "onboarding_url": onboarding_url,
            "status": "pending_onboarding",
        }
    except Exception as e:
        raise HTTPException(502, f"Stripe Connect error: {e}")


@router.get("/status")
async def connect_status(
    account_id: str,
    user: dict = Depends(get_current_user),
) -> Dict:
    """Return Connect account status (payouts_enabled, requirements)."""
    from services.stripe_connect import get_account_status

    try:
        return get_account_status(account_id)
    except Exception as e:
        raise HTTPException(502, f"Stripe Connect error: {e}")


@router.post("/payout")
async def trigger_payout(
    request: PayoutRequest,
    user: dict = Depends(get_current_user),
) -> Dict:
    """Transfer revenue share to a publisher's Connect account."""
    from services.stripe_connect import transfer_revenue

    if request.amount_cents < 72:
        raise HTTPException(400, "Minimum payout is 72¢ (70% of $1.00)")

    try:
        return transfer_revenue(
            amount_cents=request.amount_cents,
            account_id=request.publisher_account_id,
            metadata={
                "initiated_by": str(user.get("id")),
                "description": request.description or "",
            },
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"Stripe Transfer error: {e}")
