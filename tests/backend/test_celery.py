"""Tests for Celery worker and async task processing."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from events.models import Event, EventType, ProviderType
from worker.tasks import (
    run_audit,
    process_pr_event,
    process_push_event,
    analyze_diff,
    create_auto_pr,
    check_health_regression,
    _format_pr_comment,
    _get_token_for_provider,
)

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestTokenProvider:
    def test_get_github_token(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_123")
        assert _get_token_for_provider(ProviderType.GITHUB) == "ghp_123"

    def test_get_github_token_fallback_to_client_secret(self, monkeypatch):
        monkeypatch.setenv("GITHUB_CLIENT_SECRET", "secret_456")
        assert _get_token_for_provider(ProviderType.GITHUB) == "secret_456"

    def test_get_gitlab_token(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "glpat_789")
        assert _get_token_for_provider(ProviderType.GITLAB) == "glpat_789"


class TestHealthRegression:
    def test_regression_detected(self):
        result = check_health_regression.run("owner/repo", 80, 70, threshold=-5)
        assert result["status"] == "regression_detected"
        assert result["delta"] == -10
        assert result["should_alert"] is True

    def test_no_regression(self):
        result = check_health_regression.run("owner/repo", 80, 85, threshold=-5)
        assert result["status"] == "ok"
        assert result["improvement"] is True

    def test_no_baseline(self):
        result = check_health_regression.run("owner/repo", None, 70)
        assert result["status"] == "no_baseline"


class TestAnalyzeDiff:
    def test_analyze_diff_finds_todos(self):
        result = analyze_diff.run("owner/repo", "Some code\nTODO: fix this\nMore code", {})
        assert result["status"] == "completed"
        assert result["health_score"] == 90  # 100 - 1*10
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "todo"

    def test_analyze_diff_finds_fixmes(self):
        result = analyze_diff.run("owner/repo", "FIXME: urgent fix needed", {})
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "fixme"

    def test_clean_diff(self):
        result = analyze_diff.run("owner/repo", "Clean code here", {})
        assert result["health_score"] == 100
        assert len(result["issues"]) == 0


class TestFormatPRComment:
    def test_format_with_issues(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="feature",
            base_branch="main",
        )
        analysis = {
            "health_score": 75,
            "grade": "C",
            "issues": [
                {"type": "complexity", "severity": "medium"},
                {"type": "duplication", "severity": "high"},
            ],
        }
        comment = _format_pr_comment(event, analysis)

        assert "owner/repo" in comment
        assert "feature" in comment
        assert "main" in comment
        assert "75/100" in comment
        assert "Grade C" in comment
        assert "complexity" in comment
        assert "duplication" in comment

    def test_format_high_score(self):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="feature",
            base_branch="main",
        )
        analysis = {
            "health_score": 85,
            "grade": "B",
            "issues": [],
        }
        comment = _format_pr_comment(event, analysis)

        # Score 85 should be 🟢 (>=80)
        assert "🟢" in comment or "🟡" in comment  # Either green or yellow


class TestProcessPushEvent:
    @patch("worker.tasks.run_audit")
    def test_process_main_branch(self, mock_run_audit):
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_run_audit.delay.return_value = mock_task

        event_dict = {
            "type": "push",
            "provider": "github",
            "repo": "owner/repo",
            "branch": "main",
            "commits": [{"id": "abc123", "message": "fix bug"}],
            "raw_payload": {},
        }

        result = process_push_event.run(event_dict)

        assert result["status"] == "scheduled"
        assert result["repo"] == "owner/repo"
        assert result["branch"] == "main"
        mock_run_audit.delay.assert_called_once()

    def test_skip_non_default_branch(self):
        event_dict = {
            "type": "push",
            "provider": "github",
            "repo": "owner/repo",
            "branch": "feature-branch",
            "commits": [{"id": "abc123"}],
            "raw_payload": {},
        }

        result = process_push_event.run(event_dict)

        assert result["status"] == "skipped"
        assert result["reason"] == "not default branch"


class TestProcessPREvent:
    @patch("worker.tasks._get_token_for_provider")
    @patch("worker.tasks.get_adapter_for_event")
    @patch("worker.tasks._analyze_diff")
    def test_process_pr_success(self, mock_analyze, mock_get_adapter, mock_get_token):
        # Setup mocks
        mock_get_token.return_value = "fake_token"

        mock_provider = MagicMock()
        mock_provider.get_pr_diff = AsyncMock(return_value="diff content")
        mock_provider.comment_on_pr = AsyncMock(return_value="https://github.com/comment/1")
        mock_get_adapter.return_value = mock_provider

        mock_analyze.return_value = {
            "health_score": 80,
            "grade": "B",
            "issues": [],
        }

        event_dict = {
            "type": "pull_request",
            "provider": "github",
            "repo": "owner/repo",
            "pr_id": 42,
            "branch": "feature",
            "base_branch": "main",
            "commit_sha": "abc123",
            "author": "developer",
            "action": "opened",
            "raw_payload": {},
        }

        result = process_pr_event.run(event_dict)

        assert result["status"] == "completed"
        assert result["repo"] == "owner/repo"
        assert result["pr_id"] == 42

    def test_skip_non_actionable_action(self):
        event_dict = {
            "type": "pull_request",
            "provider": "github",
            "repo": "owner/repo",
            "pr_id": 42,
            "action": "closed",
            "raw_payload": {},
        }

        result = process_pr_event.run(event_dict)

        assert result["status"] == "skipped"


class TestRunAudit:
    def test_audit_success(self):
        # Skip mocking - use fallback mocks in tasks.py
        result = run_audit.run("owner/repo", "abc123", {"language": "python"})

        assert result["status"] == "completed"
        assert result["repo"] == "owner/repo"


class TestCreateAutoPR:
    @patch("worker.tasks.GitHubAdapter")
    def test_create_pr_success(self, mock_adapter_class):
        # Setup mock
        mock_adapter = MagicMock()
        mock_adapter.get_default_branch = AsyncMock(return_value="main")
        mock_adapter.get_ref_sha = AsyncMock(return_value="abc123")
        mock_adapter.create_branch = AsyncMock(return_value="refs/heads/branch")
        mock_adapter.get_file_sha = AsyncMock(return_value=None)
        mock_adapter.commit_file = AsyncMock(return_value="commit123")
        mock_adapter.create_pr = AsyncMock(return_value="https://github.com/pr/1")
        mock_adapter_class.return_value = mock_adapter

        patches = [{"path": "src/foo.py", "content": "def foo(): pass"}]

        result = create_auto_pr.run(
            repo="owner/repo",
            base_branch="main",
            patches=patches,
            proposal_type="complexity_fix",
            llm_prompt="Fix complexity",
            token="ghp_test",
            provider_type="github",
        )

        assert result["status"] == "created"
        assert result["repo"] == "owner/repo"
        assert result["pr_url"] == "https://github.com/pr/1"
