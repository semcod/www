"""Tests for auth API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]

DEMO_USER = {
    "id": 1,
    "login": "test-user",
    "name": "Test User",
    "avatar_url": "https://example.com/avatar.png",
    "github_token": "ghp_test123",
}


def _override_auth(app, user=DEMO_USER):
    from routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user


def _clear_auth(app):
    from routers.auth import get_current_user
    app.dependency_overrides.pop(get_current_user, None)


class TestSessionToken:
    """Tests for JWT session token creation and decoding."""

    def test_create_session_token(self):
        from routers.auth import create_session_token
        token = create_session_token(1)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        from routers.auth import create_session_token, decode_session_token
        token = create_session_token(42)
        payload = decode_session_token(token)
        assert payload["sub"] == "42"

    def test_decode_invalid_token(self):
        from routers.auth import decode_session_token
        with pytest.raises(Exception):
            decode_session_token("invalid.token.here")


class TestGetMe:
    """Tests for /api/me endpoint."""

    def test_get_me_authenticated(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.get("/api/me")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == 1
            assert data["login"] == "test-user"
        finally:
            _clear_auth(app)

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/me")
        assert resp.status_code == 401


class TestLogout:
    """Tests for /api/logout endpoint."""

    def test_logout(self, client):
        resp = client.post("/api/logout")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data


class TestListRepos:
    """Tests for /api/repos endpoint."""

    def test_list_repos_unauthenticated(self, client):
        resp = client.get("/api/repos")
        assert resp.status_code == 401

    def test_list_repos_no_token(self, client):
        from server import app
        user_no_token = {**DEMO_USER, "github_token": ""}
        _override_auth(app, user_no_token)
        try:
            resp = client.get("/api/repos")
            assert resp.status_code == 401
        finally:
            _clear_auth(app)

    @patch("httpx.AsyncClient")
    def test_list_repos_with_token(self, mock_client_class, client):
        from server import app
        _override_auth(app)
        try:
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {"full_name": "test/repo1", "name": "repo1", "language": "Python",
                 "stargazers_count": 10, "size": 100, "private": False, "default_branch": "main"},
            ]
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            resp = client.get("/api/repos")
            assert resp.status_code == 200
            repos = resp.json()
            assert isinstance(repos, list)
        finally:
            _clear_auth(app)


class TestGithubOAuth:
    """Tests for /auth/github redirect."""

    def test_github_oauth_redirect(self, client):
        resp = client.get("/auth/github", follow_redirects=False)
        assert resp.status_code == 307
        location = resp.headers.get("location", "")
        assert "github.com" in location


class TestGiteaOAuth:
    """Tests for /auth/gitea endpoint."""

    def test_gitea_oauth_not_configured(self, client):
        resp = client.get("/auth/gitea", follow_redirects=False)
        # Returns 501 if not configured, 307 if configured
        assert resp.status_code in (501, 307)
