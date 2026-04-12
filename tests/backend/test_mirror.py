"""Tests for mirror API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]

DEMO_USER = {
    "id": 1,
    "login": "test-user",
    "name": "Test User",
    "avatar_url": "",
    "github_token": "ghp_test",
}


def _override_auth(app, user=DEMO_USER):
    from routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user


def _clear_auth(app):
    from routers.auth import get_current_user
    app.dependency_overrides.pop(get_current_user, None)


class TestMirrorEndpoints:
    """Tests for /api/mirror endpoints."""

    def test_create_mirror_unauthenticated(self, client):
        resp = client.post("/api/mirror/create", json={
            "source_repo": "acme/app",
            "source_provider": "github",
            "target_repo": "local/app",
        })
        assert resp.status_code == 401

    def test_list_mirrors_unauthenticated(self, client):
        resp = client.get("/api/mirror/list")
        assert resp.status_code == 401

    def test_get_mirror_unauthenticated(self, client):
        resp = client.get("/api/mirror/test_id")
        assert resp.status_code == 401

    def test_delete_mirror_unauthenticated(self, client):
        resp = client.delete("/api/mirror/test_id")
        assert resp.status_code == 401

    @patch("services.mirror.MirrorService.create_mirror", new_callable=AsyncMock)
    def test_create_mirror_authenticated(self, mock_create, client):
        from server import app
        from services.mirror import MirrorStatus
        mock_create.return_value = MirrorStatus(
            mirror_id="github_acme_app",
            status="synced",
            last_sync="2026-01-01T00:00:00",
            last_commit="abc123",
            error=None,
            commits_synced=5,
        )
        _override_auth(app)
        try:
            resp = client.post("/api/mirror/create", json={
                "source_repo": "acme/app",
                "source_provider": "github",
                "target_repo": "local/app",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["mirror_id"] == "github_acme_app"
            assert data["status"] == "synced"
        finally:
            _clear_auth(app)

    def test_list_mirrors_authenticated_empty(self, client):
        from server import app
        from routers.mirror import _mirrors
        _mirrors.clear()
        _override_auth(app)
        try:
            resp = client.get("/api/mirror/list")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 0
        finally:
            _clear_auth(app)

    def test_get_mirror_not_found(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.get("/api/mirror/nonexistent")
            assert resp.status_code == 404
        finally:
            _clear_auth(app)

    def test_delete_mirror_not_found(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.delete("/api/mirror/nonexistent")
            assert resp.status_code == 404
        finally:
            _clear_auth(app)

    def test_list_mirrors_filters_by_user(self, client):
        from server import app
        from routers.mirror import _mirrors
        _mirrors.clear()
        _mirrors["mirror_a"] = {
            "source_repo": "acme/a",
            "source_provider": "github",
            "target_repo": "local/a",
            "gitea_url": "http://localhost:3000",
            "sync_interval": 3600,
            "auto_deploy": False,
            "deploy_branch": "main",
            "docker_image": None,
            "created_at": "2026-01-01T00:00:00",
            "user_id": 1,
            "last_sync": None,
            "status": "active",
        }
        _mirrors["mirror_b"] = {
            "source_repo": "other/b",
            "source_provider": "gitlab",
            "target_repo": "local/b",
            "gitea_url": "http://localhost:3000",
            "sync_interval": 3600,
            "auto_deploy": False,
            "deploy_branch": "main",
            "docker_image": None,
            "created_at": "2026-01-01T00:00:00",
            "user_id": 999,
            "last_sync": None,
            "status": "active",
        }
        _override_auth(app)
        try:
            resp = client.get("/api/mirror/list")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 1
            assert data[0]["mirror_id"] == "mirror_a"
        finally:
            _clear_auth(app)
            _mirrors.clear()

    def test_delete_mirror_wrong_user(self, client):
        from server import app
        from routers.mirror import _mirrors
        _mirrors.clear()
        _mirrors["mirror_x"] = {
            "source_repo": "other/x",
            "source_provider": "github",
            "target_repo": "local/x",
            "gitea_url": "http://localhost:3000",
            "sync_interval": 3600,
            "auto_deploy": False,
            "deploy_branch": "main",
            "docker_image": None,
            "created_at": "2026-01-01T00:00:00",
            "user_id": 999,
            "last_sync": None,
            "status": "active",
        }
        _override_auth(app)
        try:
            resp = client.delete("/api/mirror/mirror_x")
            assert resp.status_code == 403
        finally:
            _clear_auth(app)
            _mirrors.clear()
