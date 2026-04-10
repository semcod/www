"""Backend API tests for audit endpoints."""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint returns OK status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "tools" in data


def test_audit_starts_successfully():
    """Test audit endpoint creates a new audit job."""
    response = client.post(
        "/api/audit",
        json={"repo": "test-owner/test-repo", "token": "fake-token-123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data
    assert data["status"] == "running"
    assert len(data["audit_id"]) == 12  # SHA-256 hex truncated


def test_get_audit_not_found():
    """Test getting non-existent audit returns 404."""
    response = client.get("/api/audit/nonexistent123")
    assert response.status_code == 404


def test_analyze_requires_repo_url():
    """Test analyze endpoint requires repo_url."""
    response = client.post("/api/analyze", json={})
    assert response.status_code == 400
    assert "repo_url" in response.json()["detail"].lower()


def test_analyze_parses_github_url():
    """Test analyze endpoint parses GitHub URL correctly."""
    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/facebook/react", "sandbox": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data
    assert data["status"] == "running"
    assert data.get("sandbox") is True


def test_analyze_parses_gitlab_url():
    """Test analyze endpoint parses GitLab URL."""
    response = client.post(
        "/api/analyze",
        json={"repo_url": "https://gitlab.com/gitlab-org/gitlab", "sandbox": True}
    )
    assert response.status_code == 200


def test_analyze_rejects_invalid_url():
    """Test analyze endpoint rejects invalid URL."""
    response = client.post(
        "/api/analyze",
        json={"repo_url": "not-a-valid-url", "sandbox": True}
    )
    assert response.status_code == 400


def test_badge_endpoint_exists():
    """Test badge endpoint returns SVG."""
    response = client.get("/badge/test-owner-test-repo.svg")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"


def test_report_redirect():
    """Test report endpoint redirects to frontend."""
    response = client.get("/report/owner/repo", follow_redirects=False)
    assert response.status_code == 307
    assert "frontend" in response.headers["location"] or "report" in response.headers["location"]
