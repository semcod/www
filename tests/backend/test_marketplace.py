"""Tests for marketplace endpoints - preview, install, app listing."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


DEMO_USER = {"id": 1, "login": "tester", "name": "Tester", "github_token": "ghp_test"}


def _override_auth(app, user=DEMO_USER):
    from routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user


def _clear_auth(app):
    app.dependency_overrides.clear()


class TestListApps:
    def test_list_apps_returns_built_ins(self, client):
        response = client.get("/api/apps")
        assert response.status_code == 200
        apps = response.json()

        # Should have our 3 built-in apps
        names = [a["name"] for a in apps]
        assert "audit" in names
        assert "security" in names
        assert "performance" in names

    def test_apps_have_required_fields(self, client):
        response = client.get("/api/apps")
        apps = response.json()

        for app in apps:
            assert "name" in app
            assert "version" in app
            assert "triggers" in app
            assert "actions" in app
            assert "pricing" in app


class TestPreview:
    def test_preview_requires_auth(self, client):
        response = client.post("/api/preview", json={"repo": "owner/repo"})
        assert response.status_code == 401

    def test_preview_returns_score_and_comment(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.post(
                "/api/preview",
                json={"repo": "owner/repo", "provider": "github"},
            )
            assert response.status_code == 200

            data = response.json()
            assert "score" in data
            assert "comment" in data
            assert "issues" in data
            assert 0 <= data["score"] <= 100

        finally:
            _clear_auth(app)

    def test_preview_detects_issues(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.post(
                "/api/preview",
                json={"repo": "owner/bad-code", "provider": "github"},
            )
            data = response.json()
            # Preview should have mock analysis
            assert isinstance(data["issues"], list)

        finally:
            _clear_auth(app)


class TestInstall:
    def test_install_requires_auth(self, client):
        response = client.post("/api/install", json={
            "repo": "owner/repo",
            "provider": "github",
            "apps": ["audit"],
        })
        assert response.status_code == 401

    def test_install_success(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.post("/api/install", json={
                "repo": "owner/repo",
                "provider": "github",
                "apps": ["audit", "security"],
            })
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "installed"
            assert data["repo"] == "owner/repo"
            assert data["provider"] == "github"
            assert "audit" in data["apps"]

        finally:
            _clear_auth(app)

    def test_install_without_token_fails(self, client):
        from server import app
        _override_auth(app, {**DEMO_USER, "github_token": ""})
        try:
            response = client.post("/api/install", json={
                "repo": "owner/repo",
                "provider": "github",
                "apps": ["audit"],
            })
            assert response.status_code == 401

        finally:
            _clear_auth(app)


class TestListInstallations:
    def test_list_installations_requires_auth(self, client):
        response = client.get("/api/installations")
        assert response.status_code == 401

    def test_list_installations_returns_user_installs(self, client):
        from server import app
        _override_auth(app)
        try:
            # First install something
            client.post("/api/install", json={
                "repo": "owner/repo1",
                "provider": "github",
                "apps": ["audit"],
            })

            response = client.get("/api/installations")
            assert response.status_code == 200

            installs = response.json()
            assert isinstance(installs, list)
            assert any(i["repo"] == "owner/repo1" for i in installs)

        finally:
            _clear_auth(app)


class TestAppStatus:
    def test_app_status_not_installed(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.get("/api/apps/status?repo=owner/new&provider=github")
            assert response.status_code == 200

            data = response.json()
            assert data["installed"] is False
            assert data["repo"] == "owner/new"

        finally:
            _clear_auth(app)

    def test_app_status_installed(self, client):
        from server import app
        _override_auth(app)
        try:
            # Install first
            client.post("/api/install", json={
                "repo": "owner/installed",
                "provider": "github",
                "apps": ["audit"],
            })

            response = client.get("/api/apps/status?repo=owner/installed&provider=github")
            assert response.status_code == 200

            data = response.json()
            assert data["installed"] is True
            assert "audit" in data["apps"]

        finally:
            _clear_auth(app)


class TestUninstall:
    def test_uninstall_requires_auth(self, client):
        response = client.delete("/api/install?repo=owner/repo&provider=github")
        assert response.status_code == 401

    def test_uninstall_success(self, client):
        from server import app
        _override_auth(app)
        try:
            # Install first
            client.post("/api/install", json={
                "repo": "owner/to-remove",
                "provider": "github",
                "apps": ["audit"],
            })

            # Then uninstall
            response = client.delete("/api/install?repo=owner/to-remove&provider=github")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "uninstalled"

        finally:
            _clear_auth(app)

    def test_uninstall_not_found(self, client):
        from server import app
        _override_auth(app)
        try:
            response = client.delete("/api/install?repo=owner/never&provider=github")
            assert response.status_code == 404

        finally:
            _clear_auth(app)

class TestAutofixDeploy:
    """Tests for autofix deploy endpoint — verifies billing recording after fix."""

    def test_autofix_requires_auth(self, client):
        response = client.post("/api/autofix", json={
            "repo": "owner/repo",
            "provider": "github",
            "pr_id": 1,
            "base_branch": "main",
        })
        assert response.status_code == 401

    def test_autofix_requires_provider_token(self, client):
        from server import app
        _override_auth(app, {"id": 2, "login": "notoken", "github_token": ""})
        try:
            response = client.post("/api/autofix", json={
                "repo": "owner/repo",
                "provider": "github",
                "pr_id": 1,
                "base_branch": "main",
            })
            # Should fail without provider token
            assert response.status_code in (401, 402, 422)
        finally:
            _clear_auth(app)

    def test_autofix_billing_check_blocks_free_tier(self, client):
        """Verify autofix checks billing — free tier should be blocked or limited."""
        from server import app
        _override_auth(app)
        try:
            with patch("routers.marketplace.deploy._check_billing_limit", return_value=(False, "Free tier: no auto-fix allowed")):
                response = client.post("/api/autofix", json={
                    "repo": "owner/repo",
                    "provider": "github",
                    "pr_id": 1,
                    "base_branch": "main",
                })
                assert response.status_code == 402
                assert "free" in response.json()["detail"].lower() or "no auto-fix" in response.json()["detail"].lower()
        finally:
            _clear_auth(app)

    def test_autofix_billing_records_usage_when_allowed(self, client):
        """Verify billing usage is recorded when autofix is allowed (bug fix regression test)."""
        from server import app
        _override_auth(app)
        try:
            with patch("routers.marketplace.deploy._check_billing_limit", return_value=(True, "OK")), \
                 patch("routers.marketplace.deploy._record_billing_usage") as mock_record, \
                 patch("routers.marketplace.deploy._handle_mirror_if_requested", new_callable=AsyncMock), \
                 patch("services.billing.get_usage_tracker") as mock_get_tracker, \
                 patch("database.get_or_create_tenant", return_value={"id": 1, "plan": "pro"}):
                mock_tracker = MagicMock()
                mock_tracker.check_can_execute.return_value = (True, "OK")
                mock_get_tracker.return_value = mock_tracker

                mock_task_result = MagicMock(id="task-123")
                with patch("worker.tasks.create_auto_fix_pr") as mock_task:
                    mock_task.delay = MagicMock(return_value=mock_task_result)

                    response = client.post("/api/autofix", json={
                        "repo": "owner/repo",
                        "provider": "github",
                        "pr_id": 1,
                        "base_branch": "main",
                    })

                    # Should succeed (queued)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "queued"

                    # CRITICAL: billing usage must be recorded (was dead code before fix)
                    mock_record.assert_called_once()
        finally:
            _clear_auth(app)
