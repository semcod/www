"""Tests for unified adapter system and multi-platform support."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from events.models import Event, EventType, ProviderType
from adapters import (
    GitHubAdapter,
    GitLabAdapter,
    GiteaAdapter,
    parse_github_event,
    parse_gitlab_event,
    parse_gitea_event,
    get_adapter_for_event,
)

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── Event Parser Tests ─────────────────────────────────────────────────────────


class TestGitHubEventParser:
    def test_parse_pr_opened(self):
        payload = {
            "action": "opened",
            "repository": {"full_name": "owner/repo"},
            "pull_request": {
                "number": 42,
                "title": "Fix bug",
                "body": "Description",
                "head": {"ref": "feature", "sha": "abc123"},
                "base": {"ref": "main"},
                "diff_url": "https://github.com/diff",
            },
            "sender": {"login": "developer", "id": 123},
        }
        event = parse_github_event(payload)

        assert event is not None
        assert event.type == EventType.PULL_REQUEST
        assert event.provider == ProviderType.GITHUB
        assert event.repo == "owner/repo"
        assert event.pr_id == 42
        assert event.branch == "feature"
        assert event.base_branch == "main"
        assert event.author == "developer"
        assert event.action == "opened"

    def test_parse_push_event(self):
        payload = {
            "ref": "refs/heads/main",
            "repository": {"full_name": "owner/repo"},
            "commits": [{"id": "abc123", "message": "commit msg"}],
            "pusher": {"name": "developer", "email": "dev@example.com"},
            "sender": {"login": "developer"},
        }
        event = parse_github_event(payload)

        assert event is not None
        assert event.type == EventType.PUSH
        assert event.branch == "main"
        assert len(event.commits) == 1


class TestGitLabEventParser:
    def test_parse_mr_opened(self):
        payload = {
            "object_kind": "merge_request",
            "project": {"path_with_namespace": "owner/repo"},
            "object_attributes": {
                "iid": 5,
                "title": "Fix bug",
                "source_branch": "feature",
                "target_branch": "main",
                "action": "open",
                "url": "https://gitlab.com/owner/repo/-/merge_requests/5",
            },
            "user": {"username": "developer", "id": 123},
        }
        event = parse_gitlab_event(payload)

        assert event is not None
        assert event.type == EventType.PULL_REQUEST
        assert event.provider == ProviderType.GITLAB
        assert event.repo == "owner/repo"
        assert event.pr_id == 5
        assert event.branch == "feature"
        assert event.author == "developer"

    def test_parse_push_event(self):
        payload = {
            "object_kind": "push",
            "project": {"path_with_namespace": "owner/repo"},
            "ref": "refs/heads/main",
            "commits": [{"id": "abc123"}],
        }
        event = parse_gitlab_event(payload)

        assert event is not None
        assert event.type == EventType.PUSH


class TestGiteaEventParser:
    def test_parse_pr_opened(self):
        payload = {
            "action": "opened",
            "repository": {"full_name": "owner/repo"},
            "pull_request": {
                "number": 3,
                "title": "Fix bug",
                "head": {"ref": "feature", "sha": "abc123"},
                "base": {"ref": "main"},
            },
            "sender": {"login": "developer", "id": 123},
        }
        event = parse_gitea_event(payload)

        assert event is not None
        assert event.type == EventType.PULL_REQUEST
        assert event.provider == ProviderType.GITEA
        assert event.repo == "owner/repo"
        assert event.pr_id == 3


# ─── Adapter Factory Tests ──────────────────────────────────────────────────────


class TestAdapterFactory:
    def test_get_github_adapter(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
        )
        adapter = get_adapter_for_event(event, "token123")

        assert isinstance(adapter, GitHubAdapter)
        assert adapter.token == "token123"

    def test_get_gitlab_adapter(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITLAB,
            repo="owner/repo",
        )
        adapter = get_adapter_for_event(event, "token456")

        assert isinstance(adapter, GitLabAdapter)
        assert adapter.token == "token456"

    def test_get_gitea_adapter(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITEA,
            repo="owner/repo",
            raw_payload={"repository": {"html_url": "http://gitea:3000/owner/repo"}},
        )
        adapter = get_adapter_for_event(event, "token789")

        assert isinstance(adapter, GiteaAdapter)
        assert adapter.token == "token789"


# ─── GitHub Adapter Tests ─────────────────────────────────────────────────────────


class TestGitHubAdapter:
    @pytest.fixture
    def adapter(self):
        return GitHubAdapter("ghp_test_token")

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "github"

    def test_api_headers(self, adapter):
        headers = adapter.get_api_headers()
        assert "Authorization" in headers
        assert "Bearer ghp_test_token" in headers["Authorization"]
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"

    @pytest.mark.asyncio
    async def test_comment_on_pr_success(self, adapter):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"html_url": "https://github.com/comment/1"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            result = await adapter.comment_on_pr("owner/repo", 42, "Test comment")

        assert result == "https://github.com/comment/1"

    def test_webhook_signature_verification(self, adapter):
        body = b'{"test": "payload"}'
        secret = "webhook_secret"

        # Generate valid signature
        import hmac
        import hashlib

        expected_sig = "sha256=" + hmac.new(
            secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        assert adapter.verify_webhook_signature(body, expected_sig, secret) is True
        assert adapter.verify_webhook_signature(body, "invalid_sig", secret) is False


# ─── GitLab Adapter Tests ─────────────────────────────────────────────────────────


class TestGitLabAdapter:
    @pytest.fixture
    def adapter(self):
        return GitLabAdapter("glpat_test_token")

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "gitlab"

    def test_api_headers(self, adapter):
        headers = adapter.get_api_headers()
        assert "Private-Token" in headers
        assert headers["Private-Token"] == "glpat_test_token"

    def test_project_path_encoding(self, adapter):
        assert adapter._get_project_path("owner/repo") == "owner%2Frepo"
        assert adapter._get_project_path("group/subgroup/repo") == "group%2Fsubgroup%2Frepo"


# ─── Gitea Adapter Tests ──────────────────────────────────────────────────────────


class TestGiteaAdapter:
    @pytest.fixture
    def adapter(self):
        return GiteaAdapter("token123", "http://localhost:3000")

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "gitea"

    def test_api_headers(self, adapter):
        headers = adapter.get_api_headers()
        assert "Authorization" in headers
        assert "token token123" in headers["Authorization"]

    def test_api_base_url(self, adapter):
        assert adapter.api_base == "http://localhost:3000/api/v1"


# ─── Event Model Tests ────────────────────────────────────────────────────────────


class TestEventModel:
    def test_is_pr_event(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
        )
        assert event.is_pr_event() is True
        assert event.is_push_event() is False

    def test_is_push_event(self):
        event = Event(
            type=EventType.PUSH,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
        )
        assert event.is_push_event() is True
        assert event.is_pr_event() is False

    def test_get_pr_url_from_payload(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            raw_payload={"pull_request": {"html_url": "https://github.com/pr/1"}},
        )
        assert event.get_pr_url() == "https://github.com/pr/1"
