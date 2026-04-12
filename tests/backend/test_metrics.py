"""Tests for metrics API endpoints."""

import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]

MOCK_SCANS = [
    {
        "repo": "acme/backend-api",
        "health_score": 85,
        "grade": "A",
        "stats": {
            "total_files": 50,
            "total_lines": 5000,
            "languages": {"Python": 4000, "JavaScript": 1000},
            "complexity": {"cc_avg": 3.0, "functions": 100},
            "duplication": {"duplication_groups": 2, "recoverable_lines": 50},
            "quality": {"passed": 90, "warnings": 5, "errors": 1},
        },
        "completed": "2026-04-10T10:00:00+00:00",
        "badge_url": "http://localhost/badge/acme-backend-api.svg",
    },
    {
        "repo": "gitlab-org/gitlab",
        "health_score": 70,
        "grade": "B",
        "stats": {
            "total_files": 200,
            "total_lines": 20000,
            "languages": {"Ruby": 20000},
            "complexity": {"cc_avg": 5.0, "functions": 500},
            "duplication": {"duplication_groups": 10, "recoverable_lines": 200},
            "quality": {"passed": 400, "warnings": 20, "errors": 5},
        },
        "completed": "2026-04-09T10:00:00+00:00",
        "badge_url": "http://localhost/badge/gitlab-org-gitlab.svg",
    },
]


class TestStandardMetrics:
    """Tests for /api/metrics/standard endpoint."""

    @patch("routers.metrics.get_total_scan_count", return_value=2)
    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_standard_metrics_format(self, mock_recent, mock_total, client):
        resp = client.get("/api/metrics/standard")
        assert resp.status_code == 200
        data = resp.json()
        assert "meta" in data
        assert "scans" in data
        assert data["meta"]["total_scans"] == 2
        assert len(data["scans"]) == 2

    @patch("routers.metrics.get_total_scan_count", return_value=2)
    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_standard_metrics_scan_fields(self, mock_recent, mock_total, client):
        resp = client.get("/api/metrics/standard")
        data = resp.json()
        scan = data["scans"][0]
        assert "repository" in scan
        assert "platform" in scan
        assert "health_score" in scan
        assert "grade" in scan
        assert "metrics" in scan
        assert "scanned_at" in scan
        assert "badge_url" in scan

    @patch("routers.metrics.get_total_scan_count", return_value=2)
    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_standard_metrics_platform_detection(self, mock_recent, mock_total, client):
        resp = client.get("/api/metrics/standard")
        data = resp.json()
        platforms = [s["platform"] for s in data["scans"]]
        assert "github" in platforms
        assert "gitlab" in platforms

    @patch("routers.metrics.get_total_scan_count", return_value=0)
    @patch("routers.metrics.get_recent_scans", return_value=[])
    def test_standard_metrics_empty(self, mock_recent, mock_total, client):
        resp = client.get("/api/metrics/standard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["scans"] == []

    @patch("routers.metrics.get_total_scan_count", return_value=2)
    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_standard_metrics_limit(self, mock_recent, mock_total, client):
        client.get("/api/metrics/standard?limit=1")
        mock_recent.assert_called_once_with(1)


class TestMetricsSummary:
    """Tests for /api/metrics/summary endpoint."""

    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_summary_fields(self, mock_recent, client):
        resp = client.get("/api/metrics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "meta" in data
        assert "summary" in data
        summary = data["summary"]
        assert "avg_health_score" in summary
        assert "grade_distribution" in summary
        assert "total_files" in summary
        assert "total_lines" in summary
        assert "platform_distribution" in summary

    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_summary_values(self, mock_recent, client):
        resp = client.get("/api/metrics/summary")
        data = resp.json()
        summary = data["summary"]
        assert summary["avg_health_score"] == 77.5
        assert "A" in summary["grade_distribution"]
        assert "B" in summary["grade_distribution"]
        assert summary["total_files"] == 250
        assert summary["total_lines"] == 25000

    @patch("routers.metrics.get_recent_scans", return_value=[])
    def test_summary_empty(self, mock_recent, client):
        resp = client.get("/api/metrics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["avg_health_score"] == 0


class TestRepositoryMetrics:
    """Tests for /api/metrics/repository/{repo_path} endpoint."""

    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_repository_metrics_found(self, mock_recent, client):
        resp = client.get("/api/metrics/repository/acme/backend-api")
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["repository"] == "acme/backend-api"
        assert "scan" in data

    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_repository_metrics_with_platform_prefix(self, mock_recent, client):
        resp = client.get("/api/metrics/repository/github:acme/backend-api")
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["platform"] == "github"

    @patch("routers.metrics.get_recent_scans", return_value=MOCK_SCANS)
    def test_repository_metrics_not_found(self, mock_recent, client):
        resp = client.get("/api/metrics/repository/nonexistent")
        assert resp.status_code == 404
