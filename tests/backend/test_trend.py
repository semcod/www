"""Tests for trend and scan-diff API endpoints."""

import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]

SCAN_A = {
    "repo": "owner/repo",
    "health_score": 70,
    "grade": "B",
    "stats": {
        "total_files": 10,
        "total_lines": 1000,
        "complexity": {"cc_avg": 3.0, "functions": 50},
        "duplication": {"duplication_groups": 2, "recoverable_lines": 20},
        "quality": {"passed": 40, "warnings": 3, "errors": 1},
    },
    "completed": "2026-01-01T10:00:00+00:00",
    "sandbox": False,
    "badge_url": "",
}

SCAN_B = {
    "repo": "owner/repo",
    "health_score": 60,
    "grade": "C",
    "stats": {
        "total_files": 12,
        "total_lines": 1200,
        "complexity": {"cc_avg": 4.5, "functions": 55},
        "duplication": {"duplication_groups": 4, "recoverable_lines": 40},
        "quality": {"passed": 38, "warnings": 5, "errors": 3},
    },
    "completed": "2026-04-10T10:00:00+00:00",
    "sandbox": False,
    "badge_url": "",
}


class TestTrendEndpoint:
    def test_trend_returns_time_series(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A, SCAN_B]):
            response = client.get("/api/trend/owner/repo?days=365")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["repository"] == "owner/repo"
        assert len(data["points"]) == 2
        assert data["trend"]["direction"] == "degrading"
        assert data["trend"]["delta"] == -10

    def test_trend_404_no_scans(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[]):
            response = client.get("/api/trend/owner/repo")
        assert response.status_code == 404

    def test_trend_best_worst(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A, SCAN_B]):
            response = client.get("/api/trend/owner/repo?days=0")
        assert response.status_code == 200
        data = response.json()
        assert data["trend"]["best"] == 70
        assert data["trend"]["worst"] == 60


class TestTrendCompare:
    def test_compare_returns_delta(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A, SCAN_B]):
            response = client.get("/api/trend/owner/repo/compare")
        assert response.status_code == 200
        data = response.json()
        assert data["before"]["health_score"] == 70
        assert data["after"]["health_score"] == 60
        assert data["delta"]["health_score"] == -10
        assert data["delta"]["regression"] is True

    def test_compare_422_single_scan(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A]):
            response = client.get("/api/trend/owner/repo/compare")
        assert response.status_code == 422


class TestScanDiff:
    def test_diff_returns_proposals(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A, SCAN_B]):
            response = client.get("/api/scan/diff/owner/repo")
        assert response.status_code == 200
        data = response.json()
        assert data["delta"]["score_change"] == -10
        assert data["delta"]["new_issues"] > 0
        assert len(data["proposals"]) > 0
        for proposal in data["proposals"]:
            assert "type" in proposal
            assert "llm_prompt" in proposal
            assert "auto_fixable" in proposal

    def test_diff_proposals_sorted_by_impact(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A, SCAN_B]):
            response = client.get("/api/scan/diff/owner/repo")
        proposals = response.json()["proposals"]
        impacts = [p["impact"] for p in proposals]
        assert impacts == sorted(impacts, reverse=True)

    def test_diff_422_single_scan(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[SCAN_A]):
            response = client.get("/api/scan/diff/owner/repo")
        assert response.status_code == 422

    def test_diff_404_no_scans(self, client):
        with patch("routers.trend.get_repo_scans", return_value=[]):
            response = client.get("/api/scan/diff/owner/repo")
        assert response.status_code == 422
