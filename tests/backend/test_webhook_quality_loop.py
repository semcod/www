"""Tests for webhook → quality loop integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]


def _make_event(branch="main", provider="github"):
    from events.models import Event, EventType, ProviderType
    return Event(
        type=EventType.PUSH,
        provider=ProviderType(provider),
        repo="org/repo",
        branch=branch,
        commit_sha="abc123",
        author="dev",
        commits=[{"id": "abc123"}],
    )


@pytest.mark.asyncio
async def test_push_main_triggers_quality_loop():
    """Push to main should trigger the quality loop task."""
    from services.webhook_service import process_push_event

    event = _make_event(branch="main")
    provider = MagicMock()
    provider.token = "ghp_test"

    with patch("worker.tasks.quality_loop.task_on_push_quality_loop") as mock_task:
        result = await process_push_event(event, provider)
        assert result["status"] == "quality_loop_triggered"
        mock_task.delay.assert_called_once()
        call_kwargs = mock_task.delay.call_args
        assert call_kwargs.kwargs["repo"] == "org/repo"
        assert call_kwargs.kwargs["token"] == "ghp_test"
        assert call_kwargs.kwargs["provider"] == "github"


@pytest.mark.asyncio
async def test_push_master_triggers_quality_loop():
    """Push to master should also trigger the quality loop."""
    from services.webhook_service import process_push_event

    event = _make_event(branch="master")
    provider = MagicMock()
    provider.token = "ghp_test"

    with patch("worker.tasks.quality_loop.task_on_push_quality_loop") as mock_task:
        result = await process_push_event(event, provider)
        assert result["status"] == "quality_loop_triggered"
        mock_task.delay.assert_called_once()


@pytest.mark.asyncio
async def test_push_feature_branch_ignored():
    """Push to feature branch should be ignored."""
    from services.webhook_service import process_push_event

    event = _make_event(branch="feature/my-branch")
    provider = MagicMock()

    result = await process_push_event(event, provider)
    assert result["status"] == "ignored"
    assert result["reason"] == "not default branch"


@pytest.mark.asyncio
async def test_push_graceful_when_celery_unavailable():
    """Push should not fail if Celery is not available."""
    from services.webhook_service import process_push_event

    event = _make_event(branch="main")
    provider = MagicMock()
    provider.token = "ghp_test"

    with patch("worker.tasks.quality_loop.task_on_push_quality_loop", side_effect=ImportError("no celery")):
        # Should not raise
        result = await process_push_event(event, provider)
        assert result["status"] == "quality_loop_triggered"


@pytest.mark.asyncio
async def test_push_forwards_provider_token():
    """The provider token should be forwarded to the quality loop task."""
    from services.webhook_service import process_push_event

    event = _make_event(branch="main", provider="gitlab")
    provider = MagicMock()
    provider.token = "glpat_secret"

    with patch("worker.tasks.quality_loop.task_on_push_quality_loop") as mock_task:
        await process_push_event(event, provider)
        call_kwargs = mock_task.delay.call_args.kwargs
        assert call_kwargs["token"] == "glpat_secret"
        assert call_kwargs["provider"] == "gitlab"
