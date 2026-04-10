"""Tests for auto-PR generation endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]

DEMO_USER = {"id": 1, "login": "tester", "name": "Tester", "github_token": "ghp_test"}
DEMO_USER_NO_TOKEN = {"id": 2, "login": "tester2", "name": "Tester2", "github_token": ""}

PAYLOAD = {
    "repo": "owner/repo",
    "proposal_type": "complexity_regression",
    "llm_prompt": "Refactor foo() to reduce CC from 15 to 5.",
    "patches": [
        {"path": "src/foo.py", "content": "def foo():\n    pass\n"},
    ],
}


def _override_auth(app, user=DEMO_USER):
    from routers.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user


def _clear_auth(app):
    app.dependency_overrides.clear()


class TestAutoPR:
    def test_requires_auth(self, client):
        response = client.post("/api/autopr", json=PAYLOAD)
        assert response.status_code == 401

    def test_requires_github_token(self, client):
        from server import app
        _override_auth(app, DEMO_USER_NO_TOKEN)
        try:
            response = client.post("/api/autopr", json=PAYLOAD)
            assert response.status_code == 401
        finally:
            _clear_auth(app)

    def test_creates_pr_on_success(self, client):
        from server import app
        _override_auth(app)
        fake_scan = {"health_score": 70, "grade": "B", "repo": "owner/repo",
                     "stats": {}, "completed": "2026-01-01", "sandbox": False, "badge_url": ""}
        try:
            with patch("routers.autopr._get_default_branch", new_callable=AsyncMock, return_value="main"), \
                 patch("routers.autopr._get_ref_sha", new_callable=AsyncMock, return_value="abc123"), \
                 patch("routers.autopr._create_branch", new_callable=AsyncMock), \
                 patch("routers.autopr._get_file_sha", new_callable=AsyncMock, return_value=None), \
                 patch("routers.autopr._commit_file", new_callable=AsyncMock), \
                 patch("routers.autopr.get_repo_scans", return_value=[fake_scan]), \
                 patch("routers.autopr._score_improved", return_value=(70, 75)), \
                 patch("routers.autopr._create_pr", new_callable=AsyncMock, return_value="https://github.com/owner/repo/pull/1"):
                response = client.post("/api/autopr", json=PAYLOAD)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            assert data["pr_url"] == "https://github.com/owner/repo/pull/1"
            assert data["score_before"] == 70
            assert data["score_after"] == 75
        finally:
            _clear_auth(app)

    def test_rollback_creates_issue_when_score_regresses(self, client):
        from server import app
        _override_auth(app)
        try:
            with patch("routers.autopr._get_default_branch", new_callable=AsyncMock, return_value="main"), \
                 patch("routers.autopr._get_ref_sha", new_callable=AsyncMock, return_value="abc123"), \
                 patch("routers.autopr._create_branch", new_callable=AsyncMock), \
                 patch("routers.autopr._get_file_sha", new_callable=AsyncMock, return_value=None), \
                 patch("routers.autopr._commit_file", new_callable=AsyncMock), \
                 patch("routers.autopr._score_improved", return_value=(75, 60)), \
                 patch("routers.autopr._create_issue", new_callable=AsyncMock, return_value="https://github.com/owner/repo/issues/5"):
                response = client.post("/api/autopr", json=PAYLOAD)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "rolled_back"
            assert data["issue_url"] == "https://github.com/owner/repo/issues/5"
            assert data["rollback_reason"] is not None
            assert "regressed" in data["rollback_reason"]
        finally:
            _clear_auth(app)

    def test_pr_created_when_no_scan_history(self, client):
        from server import app
        _override_auth(app)
        try:
            with patch("routers.autopr._get_default_branch", new_callable=AsyncMock, return_value="main"), \
                 patch("routers.autopr._get_ref_sha", new_callable=AsyncMock, return_value="abc123"), \
                 patch("routers.autopr._create_branch", new_callable=AsyncMock), \
                 patch("routers.autopr._get_file_sha", new_callable=AsyncMock, return_value=None), \
                 patch("routers.autopr._commit_file", new_callable=AsyncMock), \
                 patch("routers.autopr._score_improved", return_value=(None, None)), \
                 patch("routers.autopr._create_pr", new_callable=AsyncMock, return_value="https://github.com/owner/repo/pull/2"):
                response = client.post("/api/autopr", json=PAYLOAD)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
        finally:
            _clear_auth(app)

    def test_multiple_patches_committed(self, client):
        from server import app
        _override_auth(app)
        multi_payload = {**PAYLOAD, "patches": [
            {"path": "src/a.py", "content": "# a"},
            {"path": "src/b.py", "content": "# b"},
        ]}
        commit_mock = AsyncMock()
        try:
            with patch("routers.autopr._get_default_branch", new_callable=AsyncMock, return_value="main"), \
                 patch("routers.autopr._get_ref_sha", new_callable=AsyncMock, return_value="abc123"), \
                 patch("routers.autopr._create_branch", new_callable=AsyncMock), \
                 patch("routers.autopr._get_file_sha", new_callable=AsyncMock, return_value=None), \
                 patch("routers.autopr._commit_file", commit_mock), \
                 patch("routers.autopr._score_improved", return_value=(None, None)), \
                 patch("routers.autopr._create_pr", new_callable=AsyncMock, return_value="https://github.com/owner/repo/pull/3"):
                response = client.post("/api/autopr", json=multi_payload)
            assert response.status_code == 200
            assert commit_mock.call_count == 2
        finally:
            _clear_auth(app)

    def test_branch_name_includes_prefix(self, client):
        from server import app
        _override_auth(app)
        payload = {**PAYLOAD, "branch_prefix": "hotfix"}
        try:
            with patch("routers.autopr._get_default_branch", new_callable=AsyncMock, return_value="main"), \
                 patch("routers.autopr._get_ref_sha", new_callable=AsyncMock, return_value="abc123"), \
                 patch("routers.autopr._create_branch", new_callable=AsyncMock), \
                 patch("routers.autopr._get_file_sha", new_callable=AsyncMock, return_value=None), \
                 patch("routers.autopr._commit_file", new_callable=AsyncMock), \
                 patch("routers.autopr._score_improved", return_value=(None, None)), \
                 patch("routers.autopr._create_pr", new_callable=AsyncMock, return_value="https://github.com/owner/repo/pull/4"):
                response = client.post("/api/autopr", json=payload)
            data = response.json()
            assert data["branch"].startswith("hotfix-")
        finally:
            _clear_auth(app)


class TestBodyBuilders:
    def test_pr_body_contains_score_table(self):
        from routers.autopr import _build_pr_body, AutoPRRequest, PatchFile
        req = AutoPRRequest(
            repo="owner/repo",
            proposal_type="complexity_regression",
            llm_prompt="Reduce CC.",
            patches=[PatchFile(path="src/foo.py", content="")],
        )
        body = _build_pr_body(req, "abc123", 70, 78)
        assert "70" in body
        assert "78" in body
        assert "+8" in body
        assert "complexity_regression" in body

    def test_issue_body_contains_reason(self):
        from routers.autopr import _build_issue_body, AutoPRRequest, PatchFile
        req = AutoPRRequest(
            repo="owner/repo",
            proposal_type="duplication_increase",
            llm_prompt="Remove duplication.",
            patches=[PatchFile(path="src/foo.py", content="")],
        )
        body = _build_issue_body(req, "xyz999", "score regressed badly", 80, 60)
        assert "regressed badly" in body
        assert "duplication_increase" in body
        assert "src/foo.py" in body
