from fastapi.testclient import TestClient

import routers.auth as auth_module
from server import app


client = TestClient(app)


class _MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _MockAsyncClient:
    def __init__(self, payload):
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, *args, **kwargs):
        return _MockResponse(self._payload)


def test_github_oauth_start_redirects_to_github():
    response = client.get("/auth/github", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert "github.com/login/oauth/authorize" in response.headers["location"]
    assert "redirect_uri=" in response.headers["location"]


def test_github_oauth_callback_redirects_to_frontend(monkeypatch):
    monkeypatch.setattr(
        auth_module.httpx,
        "AsyncClient",
        lambda: _MockAsyncClient({"access_token": "gho_test_token"}),
    )

    response = client.get("/auth/callback?code=test-code", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"].endswith("/audit?token=gho_test_token")


def test_github_oauth_callback_returns_400_without_token(monkeypatch):
    monkeypatch.setattr(
        auth_module.httpx,
        "AsyncClient",
        lambda: _MockAsyncClient({}),
    )

    response = client.get("/auth/callback?code=test-code", follow_redirects=False)

    assert response.status_code == 400
    assert response.json()["detail"] == "OAuth failed"
