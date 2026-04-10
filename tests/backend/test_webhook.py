"""Webhook handler tests."""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_webhook_without_signature_ignored():
    """Test webhook without signature is processed (no secret set)."""
    response = client.post(
        "/webhook/github",
        json={"action": "opened", "number": 1, "pull_request": {"id": 123}},
        headers={"X-GitHub-Event": "pull_request"}
    )
    # Should not crash, may return processing or ignored
    assert response.status_code in [200, 202]


def test_webhook_installation_event():
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
