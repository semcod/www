"""Tests for marketplace quality report endpoint."""
import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


def test_marketplace_quality_from_badge_cache(client):
    cached = {"score": 92, "grade": "A+", "updated": "2026-04-12T10:00:00Z", "weekly_issues": 0}
    with patch("routers.marketplace.quality.get_badge_cache", return_value=cached):
        resp = client.get("/api/marketplace/org/repo/quality")
        assert resp.status_code == 200
        data = resp.json()
        assert data["grade"] == "A+"
        assert data["score"] == 92
        assert data["badge_url"] == "/badge/org-repo.svg"


def test_marketplace_quality_from_scans(client):
    scans = [
        {"health_score": 70, "grade": "B+", "completed": "2026-04-10T10:00:00Z", "stats": {"cc": 3.2}},
        {"health_score": 78, "grade": "B+", "completed": "2026-04-12T10:00:00Z", "stats": {"cc": 2.9}},
    ]
    with patch("routers.marketplace.quality.get_badge_cache", return_value=None), \
         patch("routers.marketplace.quality.get_repo_scans", return_value=scans):
        resp = client.get("/api/marketplace/org/repo/quality")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 78
        assert data["trend"] == "improving"
        assert data["scan_count"] == 2


def test_marketplace_quality_no_data_404(client):
    with patch("routers.marketplace.quality.get_badge_cache", return_value=None), \
         patch("routers.marketplace.quality.get_repo_scans", return_value=[]):
        resp = client.get("/api/marketplace/org/unknown/quality")
        assert resp.status_code == 404


def test_marketplace_quality_degrading_trend(client):
    scans = [
        {"health_score": 85, "grade": "A", "completed": "2026-04-10T10:00:00Z", "stats": {}},
        {"health_score": 60, "grade": "B", "completed": "2026-04-12T10:00:00Z", "stats": {}},
    ]
    with patch("routers.marketplace.quality.get_badge_cache", return_value=None), \
         patch("routers.marketplace.quality.get_repo_scans", return_value=scans):
        resp = client.get("/api/marketplace/org/repo/quality")
        data = resp.json()
        assert data["trend"] == "degrading"
