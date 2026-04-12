"""Tests for webhook_v2 API endpoints."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestGithubWebhook:
    """Tests for /v2/webhook/github endpoint."""

    @patch("routers.webhook_v2.verify_github_signature", return_value=True)
    @patch("routers.webhook_v2.parse_github_webhook")
    def test_github_webhook_ping(self, mock_parse, mock_verify, client):
        """GitHub ping event returns ignored."""
        mock_parse.return_value = None
        resp = client.post(
            "/v2/webhook/github",
            json={"zen": "Design for failure."},
            headers={"X-GitHub-Event": "ping"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ignored"

    @patch("routers.webhook_v2._get_token_for_provider", return_value="ghp_test")
    @patch("routers.webhook_v2.parse_github_webhook")
    @patch("routers.webhook_v2.verify_github_signature", return_value=True)
    def test_github_webhook_pr_event(self, mock_verify, mock_parse, mock_token, client):
        """GitHub PR event returns processing."""
        from events.models import Event, EventType, ProviderType
        mock_parse.return_value = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="main",
            commit_sha="abc123",
            author="dev",
        )
        resp = client.post(
            "/v2/webhook/github",
            json={"action": "opened", "number": 1},
            headers={"X-GitHub-Event": "pull_request"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"
        assert data["event"] == "pull_request"

    @patch("routers.webhook_v2._get_token_for_provider", return_value="ghp_test")
    @patch("routers.webhook_v2.parse_github_webhook")
    @patch("routers.webhook_v2.verify_github_signature", return_value=True)
    def test_github_webhook_push_event(self, mock_verify, mock_parse, mock_token, client):
        """GitHub push event returns processing."""
        from events.models import Event, EventType, ProviderType
        mock_parse.return_value = Event(
            type=EventType.PUSH,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="main",
            commit_sha="abc123",
            author="dev",
        )
        resp = client.post(
            "/v2/webhook/github",
            json={"ref": "refs/heads/main"},
            headers={"X-GitHub-Event": "push"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"
        assert data["event"] == "push"

    @patch("routers.webhook_v2._get_token_for_provider", return_value=None)
    @patch("routers.webhook_v2.parse_github_webhook")
    @patch("routers.webhook_v2.verify_github_signature", return_value=True)
    def test_github_webhook_no_token(self, mock_verify, mock_parse, mock_token, client):
        """GitHub webhook with no token returns ignored."""
        from events.models import Event, EventType, ProviderType
        mock_parse.return_value = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="main",
            commit_sha="abc123",
            author="dev",
        )
        resp = client.post(
            "/v2/webhook/github",
            json={"action": "opened"},
            headers={"X-GitHub-Event": "pull_request"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ignored"


class TestGitlabWebhook:
    """Tests for /v2/webhook/gitlab endpoint."""

    @patch("routers.webhook_v2.parse_gitlab_webhook")
    def test_gitlab_webhook_ping(self, mock_parse, client):
        """GitLab ping event returns ignored."""
        mock_parse.return_value = None
        resp = client.post(
            "/v2/webhook/gitlab",
            json={"object_kind": "push"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ignored"

    @patch("routers.webhook_v2.parse_gitlab_webhook")
    @patch("routers.webhook_v2._get_token_for_provider", return_value="glpat_test")
    def test_gitlab_webhook_push_event(self, mock_token, mock_parse, client):
        """GitLab push event returns processing."""
        from events.models import Event, EventType, ProviderType
        mock_parse.return_value = Event(
            type=EventType.PUSH,
            provider=ProviderType.GITLAB,
            repo="gitlab-org/gitlab",
            branch="main",
            commit_sha="def456",
            author="dev",
        )
        resp = client.post(
            "/v2/webhook/gitlab",
            json={"object_kind": "push"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"


class TestGiteaWebhook:
    """Tests for /v2/webhook/gitea endpoint."""

    @patch("routers.webhook_v2.verify_gitea_signature", return_value=True)
    @patch("routers.webhook_v2.parse_gitea_webhook")
    def test_gitea_webhook_ping(self, mock_parse, mock_verify, client):
        """Gitea ping event returns ignored."""
        mock_parse.return_value = None
        resp = client.post(
            "/v2/webhook/gitea",
            json={},
            headers={"X-Gitea-Event": "push"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ignored"

    @patch("routers.webhook_v2._get_token_for_provider", return_value="gitea_test")
    @patch("routers.webhook_v2.parse_gitea_webhook")
    @patch("routers.webhook_v2.verify_gitea_signature", return_value=True)
    def test_gitea_webhook_push_event(self, mock_verify, mock_parse, mock_token, client):
        """Gitea push event returns processing."""
        from events.models import Event, EventType, ProviderType
        mock_parse.return_value = Event(
            type=EventType.PUSH,
            provider=ProviderType.GITEA,
            repo="local/app",
            branch="main",
            commit_sha="ghi789",
            author="dev",
        )
        resp = client.post(
            "/v2/webhook/gitea",
            json={"ref": "refs/heads/main"},
            headers={"X-Gitea-Event": "push"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"


class TestTokenProvider:
    """Tests for _get_token_for_provider helper."""

    def test_github_token(self):
        from routers.webhook_v2 import _get_token_for_provider
        from events.models import ProviderType
        result = _get_token_for_provider(ProviderType.GITHUB)
        # Returns whatever is configured or None
        assert result is None or isinstance(result, str)

    def test_gitlab_token(self):
        from routers.webhook_v2 import _get_token_for_provider
        from events.models import ProviderType
        result = _get_token_for_provider(ProviderType.GITLAB)
        assert result is None or isinstance(result, str)

    def test_gitea_token(self):
        from routers.webhook_v2 import _get_token_for_provider
        from events.models import ProviderType
        result = _get_token_for_provider(ProviderType.GITEA)
        assert result is None or isinstance(result, str)
