"""Tests for ecosystem dashboard router."""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── GET /api/ecosystem ──────────────────────────────────────────────────────

def test_ecosystem_empty(client):
    with patch("routers.ecosystem.get_recent_scans", return_value=[]):
        resp = client.get("/api/ecosystem")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects"] == 0
        assert data["projects"] == []
        assert data["avg_health"] is None


def test_ecosystem_single_project(client):
    scans = [
        {"repo": "org/alpha", "health_score": 82, "grade": "A", "completed": "2026-04-12T10:00:00Z", "badge_url": "/badge/org-alpha.svg", "stats": {}, "sandbox": False},
    ]
    with patch("routers.ecosystem.get_recent_scans", return_value=scans):
        resp = client.get("/api/ecosystem")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects"] == 1
        assert data["projects"][0]["name"] == "org/alpha"
        assert data["projects"][0]["health_score"] == 82
        assert data["projects"][0]["trend"] == "stable"
        assert data["avg_health"] == 82.0


def test_ecosystem_multiple_projects_sorted_by_health(client):
    scans = [
        {"repo": "org/alpha", "health_score": 90, "grade": "A", "completed": "2026-04-12T10:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
        {"repo": "org/beta", "health_score": 55, "grade": "C", "completed": "2026-04-12T09:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
    ]
    with patch("routers.ecosystem.get_recent_scans", return_value=scans):
        resp = client.get("/api/ecosystem")
        data = resp.json()
        assert data["total_projects"] == 2
        # Worst health first in priority ranking
        assert data["priority_ranking"][0] == "org/beta"
        assert data["priority_ranking"][1] == "org/alpha"


def test_ecosystem_trend_detection(client):
    scans = [
        {"repo": "org/alpha", "health_score": 60, "grade": "B", "completed": "2026-04-12T10:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
        {"repo": "org/alpha", "health_score": 70, "grade": "B+", "completed": "2026-04-11T10:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
    ]
    with patch("routers.ecosystem.get_recent_scans", return_value=scans):
        resp = client.get("/api/ecosystem")
        data = resp.json()
        # health dropped 70→60 = -10 → degrading
        assert data["projects"][0]["trend"] == "degrading"


# ─── GET /api/ecosystem/{owner}/{repo}/history ───────────────────────────────

def test_ecosystem_project_history(client):
    scans = [
        {"repo": "org/alpha", "health_score": 70, "grade": "B+", "completed": "2026-04-10T10:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
        {"repo": "org/alpha", "health_score": 82, "grade": "A", "completed": "2026-04-12T10:00:00Z", "badge_url": "", "stats": {}, "sandbox": False},
    ]
    with patch("routers.ecosystem.get_repo_scans", return_value=scans):
        resp = client.get("/api/ecosystem/org/alpha/history?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["repo"] == "org/alpha"
        assert data["total_scans"] == 2
        assert len(data["history"]) == 2


def test_ecosystem_project_history_empty(client):
    with patch("routers.ecosystem.get_repo_scans", return_value=[]):
        resp = client.get("/api/ecosystem/org/unknown/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_scans"] == 0
        assert data["history"] == []
