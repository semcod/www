"""Tests for Stripe billing endpoints and subscription helpers."""

import json
import pytest
from unittest.mock import MagicMock, patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]

# ─── Auth helper ──────────────────────────────────────────────────────────────

DEMO_USER = {"id": 9001, "login": "test-user", "name": "Test", "avatar_url": "", "github_token": ""}


def _override_auth(app):
    """Override get_current_user dependency on the app for the duration of a test."""
    from routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: DEMO_USER
    return app


def _clear_auth(app):
    app.dependency_overrides.clear()


# ─── Plans ────────────────────────────────────────────────────────────────────

class TestPlans:
    def test_list_plans_no_auth(self, client):
        response = client.get("/api/billing/plans")
        assert response.status_code == 200
        data = response.json()
        assert "free" in data
        assert "pro" in data
        assert "team" in data
        assert data["free"]["scans_per_week"] == 3
        assert data["pro"]["scans_per_week"] == -1

    def test_plans_have_pricing(self, client):
        data = client.get("/api/billing/plans").json()
        assert data["pro"]["price_monthly"] == 9
        assert data["pro"]["price_annual"] == 81
        assert data["team"]["price_monthly"] == 29


# ─── Billing status ───────────────────────────────────────────────────────────

class TestBillingStatus:
    def test_status_free_user(self, client):
        from server import app
        _override_auth(app)
        try:
            with patch("routers.billing.get_subscription", return_value=None):
                response = client.get("/api/billing/status")
            assert response.status_code == 200
            data = response.json()
            assert data["plan"] == "free"
            assert data["scans_per_week"] == 3
            assert data["scans_remaining"] == 3
        finally:
            _clear_auth(app)

    def test_status_pro_user_unlimited(self, client):
        from server import app
        _override_auth(app)
        sub = {"plan": "pro", "status": "active", "scans_this_week": 10,
               "stripe_customer_id": "cus_x", "stripe_subscription_id": "sub_x"}
        try:
            with patch("routers.billing.get_subscription", return_value=sub):
                response = client.get("/api/billing/status")
            assert response.status_code == 200
            data = response.json()
            assert data["plan"] == "pro"
            assert data["scans_remaining"] is None
        finally:
            _clear_auth(app)

    def test_status_free_at_limit(self, client):
        from server import app
        _override_auth(app)
        sub = {"plan": "free", "status": "active", "scans_this_week": 3,
               "stripe_customer_id": "", "stripe_subscription_id": ""}
        try:
            with patch("routers.billing.get_subscription", return_value=sub):
                response = client.get("/api/billing/status")
            data = response.json()
            assert data["scans_remaining"] == 0
        finally:
            _clear_auth(app)


# ─── Checkout ─────────────────────────────────────────────────────────────────

class TestCheckout:
    def test_checkout_creates_stripe_session(self, client):
        from server import app
        _override_auth(app)
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test-session"
        mock_client = MagicMock()
        mock_client.checkout.sessions.create.return_value = mock_session
        try:
            with patch("routers.billing.get_subscription", return_value=None), \
                 patch("routers.billing._stripe_client", return_value=mock_client):
                from routers.billing import PLANS
                PLANS["pro"]["stripe_price_monthly"] = "price_test_pro_monthly"
                response = client.post("/api/billing/checkout", json={"plan": "pro", "billing": "monthly"})
            assert response.status_code == 200
            assert "url" in response.json()
            assert "stripe.com" in response.json()["url"]
        finally:
            _clear_auth(app)

    def test_checkout_free_plan_returns_400(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.post("/api/billing/checkout", json={"plan": "free", "billing": "monthly"})
            assert response.status_code == 400
        finally:
            _clear_auth(app)

    def test_checkout_invalid_plan_returns_400(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.post("/api/billing/checkout", json={"plan": "enterprise", "billing": "monthly"})
            assert response.status_code == 400
        finally:
            _clear_auth(app)


# ─── Stripe webhook ───────────────────────────────────────────────────────────

class TestWebhook:
    def _make_event(self, event_type: str, data: dict) -> bytes:
        return json.dumps({
            "type": event_type,
            "data": {"object": data},
        }).encode()

    def test_webhook_invalid_signature_returns_400(self, client):
        with patch("routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"):
            response = client.post(
                "/api/billing/webhook",
                content=b"{}",
                headers={"stripe-signature": "bad-sig", "Content-Type": "application/json"},
            )
        assert response.status_code == 400

    def test_webhook_checkout_completed_activates_subscription(self, client):
        payload = self._make_event("checkout.session.completed", {
            "metadata": {"user_id": "42", "plan": "pro"},
            "customer": "cus_abc",
            "subscription": "sub_abc",
        })
        with patch("routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct, \
             patch("routers.billing.upsert_subscription") as mock_upsert:
            mock_construct.return_value = {
                "type": "checkout.session.completed",
                "data": {"object": {
                    "metadata": {"user_id": "42", "plan": "pro"},
                    "customer": "cus_abc",
                    "subscription": "sub_abc",
                }},
            }
            response = client.post(
                "/api/billing/webhook",
                content=payload,
                headers={"stripe-signature": "sig", "Content-Type": "application/json"},
            )
        assert response.status_code == 200
        mock_upsert.assert_called_once_with(42, "pro", "cus_abc", "sub_abc", "active")

    def test_webhook_subscription_deleted_downgrades_to_free(self, client):
        sub_row = {"user_id": 42, "plan": "pro", "stripe_customer_id": "cus_abc",
                   "stripe_subscription_id": "sub_abc", "status": "active", "scans_this_week": 0,
                   "week_reset_at": ""}
        with patch("routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct, \
             patch("routers.billing._find_sub_by_customer", return_value=sub_row), \
             patch("routers.billing.upsert_subscription") as mock_upsert:
            mock_construct.return_value = {
                "type": "customer.subscription.deleted",
                "data": {"object": {"customer": "cus_abc", "id": "sub_abc"}},
            }
            response = client.post(
                "/api/billing/webhook",
                content=b"{}",
                headers={"stripe-signature": "sig", "Content-Type": "application/json"},
            )
        assert response.status_code == 200
        mock_upsert.assert_called_once_with(42, "free", "cus_abc", "", "cancelled")


# ─── Scan gate ────────────────────────────────────────────────────────────────

class TestScanGate:
    def test_allowed_when_under_limit(self):
        from routers.billing import check_scan_allowed
        sub = {"plan": "free", "status": "active", "scans_this_week": 1,
               "stripe_customer_id": "", "stripe_subscription_id": ""}
        with patch("routers.billing.get_subscription", return_value=sub), \
             patch("routers.billing.increment_scan_count"):
            check_scan_allowed(1)  # should not raise

    def test_blocked_when_at_limit(self):
        from routers.billing import check_scan_allowed
        from fastapi import HTTPException
        sub = {"plan": "free", "status": "active", "scans_this_week": 3,
               "stripe_customer_id": "", "stripe_subscription_id": ""}
        with patch("routers.billing.get_subscription", return_value=sub):
            with pytest.raises(HTTPException) as exc_info:
                check_scan_allowed(1)
        assert exc_info.value.status_code == 402

    def test_unlimited_for_pro(self):
        from routers.billing import check_scan_allowed
        sub = {"plan": "pro", "status": "active", "scans_this_week": 999,
               "stripe_customer_id": "cus_x", "stripe_subscription_id": "sub_x"}
        with patch("routers.billing.get_subscription", return_value=sub):
            check_scan_allowed(1)  # should not raise


# ─── DB helpers ───────────────────────────────────────────────────────────────

import time as _time
_TS = int(_time.time() * 1000) % 900000


class TestSubscriptionDB:
    def test_increment_creates_row_for_new_user(self):
        from database import increment_scan_count, get_subscription
        user_id = 90000 + _TS + 1
        count = increment_scan_count(user_id)
        assert count == 1
        sub = get_subscription(user_id)
        assert sub["scans_this_week"] == 1
        assert sub["plan"] == "free"

    def test_increment_accumulates(self):
        from database import increment_scan_count
        user_id = 90000 + _TS + 2
        increment_scan_count(user_id)
        count = increment_scan_count(user_id)
        assert count == 2

    def test_upsert_subscription_creates_and_updates(self):
        from database import upsert_subscription, get_subscription
        user_id = 90000 + _TS + 3
        upsert_subscription(user_id, "pro", "cus_test", "sub_test", "active")
        sub = get_subscription(user_id)
        assert sub["plan"] == "pro"
        assert sub["stripe_customer_id"] == "cus_test"

        upsert_subscription(user_id, "free", "", "", "cancelled")
        sub = get_subscription(user_id)
        assert sub["plan"] == "free"
        assert sub["status"] == "cancelled"
