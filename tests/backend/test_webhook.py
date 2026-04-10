"""Webhook handler tests."""

from typing import Any

import pytest

pytestmark = [pytest.mark.fast, pytest.mark.unit]


def test_webhook_without_signature_ignored(client):
    """Test webhook without signature is processed (no secret set)."""
    response = client.post(
        "/webhook/github",
        json={"action": "opened", "number": 1, "pull_request": {"id": 123}},
        headers={"X-GitHub-Event": "pull_request"}
    )
    # Should not crash, may return processing or ignored
    assert response.status_code in [200, 202]


def test_webhook_installation_event(client):
    """Test installation created webhook."""
    payload = {
        "action": "created",
        "installation": {"id": 12345},
        "sender": {"login": "testuser"}
    }
    response = client.post(
        "/webhook/github",
        json=payload,
        headers={"X-GitHub-Event": "installation"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "installed"
