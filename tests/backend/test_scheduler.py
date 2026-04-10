"""Tests for scheduled scans API and scan_job helpers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── Schedule API ─────────────────────────────────────────────────────────────

class TestScheduleAPI:
    def test_list_empty(self, client):
        response = client.get("/api/schedules")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_schedule(self, client):
        response = client.post("/api/schedules", json={
            "repo": "test/create-repo",
            "interval_hours": 2.0,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["repo"] == "test/create-repo"
        assert data["interval_hours"] == 2.0
        assert "created_at" in data

    def test_create_duplicate_returns_409(self, client):
        client.post("/api/schedules", json={"repo": "test/dup-repo", "interval_hours": 1.0})
        response = client.post("/api/schedules", json={"repo": "test/dup-repo", "interval_hours": 1.0})
        assert response.status_code == 409

    def test_get_existing_schedule(self, client):
        client.post("/api/schedules", json={"repo": "test/get-repo", "interval_hours": 3.0})
        response = client.get("/api/schedules/test/get-repo")
        assert response.status_code == 200
        assert response.json()["repo"] == "test/get-repo"

    def test_get_missing_returns_404(self, client):
        response = client.get("/api/schedules/nobody/nothing")
        assert response.status_code == 404

    def test_update_schedule(self, client):
        client.post("/api/schedules", json={"repo": "test/upd-repo", "interval_hours": 1.0})
        response = client.patch("/api/schedules/test/upd-repo", json={
            "repo": "test/upd-repo",
            "interval_hours": 6.0,
        })
        assert response.status_code == 200
        assert response.json()["interval_hours"] == 6.0

    def test_update_missing_returns_404(self, client):
        response = client.patch("/api/schedules/nobody/x", json={
            "repo": "nobody/x",
            "interval_hours": 1.0,
        })
        assert response.status_code == 404

    def test_delete_schedule(self, client):
        client.post("/api/schedules", json={"repo": "test/del-repo", "interval_hours": 1.0})
        response = client.delete("/api/schedules/test/del-repo")
        assert response.status_code == 204
        assert client.get("/api/schedules/test/del-repo").status_code == 404

    def test_delete_missing_returns_404(self, client):
        response = client.delete("/api/schedules/nobody/nothing2")
        assert response.status_code == 404

    def test_list_shows_created_schedules(self, client):
        client.post("/api/schedules", json={"repo": "test/list-repo", "interval_hours": 1.0})
        response = client.get("/api/schedules")
        assert response.status_code == 200
        repos = [s["repo"] for s in response.json()]
        assert "test/list-repo" in repos


# ─── scan_job helpers ─────────────────────────────────────────────────────────

class TestDetectDegradation:
    def test_no_degradation_when_score_stable(self):
        from scheduler.scan_job import _detect_degradation
        scans = [
            {"health_score": 80, "repo": "r", "grade": "A", "stats": {}, "completed": "2026-01-01", "sandbox": False, "badge_url": ""},
            {"health_score": 78, "repo": "r", "grade": "B", "stats": {}, "completed": "2026-01-02", "sandbox": False, "badge_url": ""},
        ]
        with patch("scheduler.scan_job.get_repo_scans", return_value=scans):
            alert = _detect_degradation("r", 78)
        assert alert is None

    def test_degradation_detected_on_large_drop(self):
        from scheduler.scan_job import _detect_degradation
        scans = [
            {"health_score": 80, "repo": "r", "grade": "A", "stats": {}, "completed": "2026-01-01", "sandbox": False, "badge_url": ""},
            {"health_score": 80, "repo": "r", "grade": "A", "stats": {}, "completed": "2026-01-02", "sandbox": False, "badge_url": ""},
        ]
        with patch("scheduler.scan_job.get_repo_scans", return_value=scans):
            alert = _detect_degradation("r", 70)
        assert alert is not None
        assert alert["delta"] == -10
        assert alert["prev_score"] == 80
        assert alert["new_score"] == 70

    def test_no_alert_when_single_scan(self):
        from scheduler.scan_job import _detect_degradation
        scans = [
            {"health_score": 80, "repo": "r", "grade": "A", "stats": {}, "completed": "2026-01-01", "sandbox": False, "badge_url": ""},
        ]
        with patch("scheduler.scan_job.get_repo_scans", return_value=scans):
            alert = _detect_degradation("r", 60)
        assert alert is None


class TestFireAlert:
    @pytest.mark.asyncio
    async def test_no_webhook_logs_warning(self, caplog):
        from scheduler.scan_job import _fire_alert
        import logging
        with caplog.at_level(logging.WARNING):
            await _fire_alert({"repo": "r", "prev_score": 80, "new_score": 70, "delta": -10, "detected_at": "now"}, None)
        assert "no webhook" in caplog.text.lower() or "Degradation" in caplog.text

    @pytest.mark.asyncio
    async def test_fires_post_to_webhook(self):
        from scheduler.scan_job import _fire_alert
        import httpx
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.post = AsyncMock(return_value=mock_response)
            await _fire_alert(
                {"repo": "r", "prev_score": 80, "new_score": 70, "delta": -10, "detected_at": "now"},
                "https://hooks.slack.com/test",
            )
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert "hooks.slack.com" in call_kwargs[0][0]
