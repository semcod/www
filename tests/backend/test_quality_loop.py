"""Tests for the webhook-triggered quality loop task."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── _run_quality_loop tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_quality_loop_skips_when_redsl_unavailable():
    from worker.tasks.quality_loop import _run_quality_loop

    mock_redsl = AsyncMock()
    mock_redsl.health = AsyncMock(return_value=False)

    with patch("services.redsl_client.RedslClient", return_value=mock_redsl):
        result = await _run_quality_loop("org/repo", "abc123", "/tmp/repo", "", "github")
        assert result["status"] == "skipped"
        assert result["reason"] == "redsl_unavailable"


@pytest.mark.asyncio
async def test_quality_loop_healthy_no_action():
    from worker.tasks.quality_loop import _run_quality_loop

    mock_redsl = AsyncMock()
    mock_redsl.health = AsyncMock(return_value=True)
    mock_redsl.health_score = AsyncMock(return_value={"score": 85, "grade": "A", "dimensions": {}})

    with patch("services.redsl_client.RedslClient", return_value=mock_redsl), \
         patch("worker.tasks.quality_loop._save_health_snapshot"), \
         patch("worker.tasks.quality_loop._check_health_drop"):
        result = await _run_quality_loop("org/repo", "abc123", "/tmp/repo", "", "github")
        assert result["status"] == "healthy"
        assert result["score"] == 85


@pytest.mark.asyncio
async def test_quality_loop_triggers_refactor_below_threshold():
    from worker.tasks.quality_loop import _run_quality_loop

    mock_redsl = AsyncMock()
    mock_redsl.health = AsyncMock(return_value=True)
    mock_redsl.health_score = AsyncMock(return_value={"score": 45, "grade": "D", "dimensions": {}})
    mock_redsl.cycle = AsyncMock(return_value={"proposals_applied": 2, "files_modified": ["a.py", "b.py"]})

    with patch("services.redsl_client.RedslClient", return_value=mock_redsl), \
         patch("worker.tasks.quality_loop._save_health_snapshot"), \
         patch("worker.tasks.quality_loop._check_health_drop"), \
         patch("worker.tasks.quality_loop._create_quality_ticket", return_value="ticket-123"), \
         patch("worker.tasks.quality_loop._update_ticket_status"), \
         patch("worker.tasks.quality_loop._update_badge_cache"):
        result = await _run_quality_loop("org/repo", "abc123", "/tmp/repo", "", "github")
        assert result["status"] == "refactored"
        assert result["proposals_applied"] == 2
        assert result["ticket_id"] == "ticket-123"


@pytest.mark.asyncio
async def test_quality_loop_no_changes_applied():
    from worker.tasks.quality_loop import _run_quality_loop

    mock_redsl = AsyncMock()
    mock_redsl.health = AsyncMock(return_value=True)
    mock_redsl.health_score = AsyncMock(return_value={"score": 55, "grade": "C", "dimensions": {}})
    mock_redsl.cycle = AsyncMock(return_value={"proposals_applied": 0, "files_modified": []})

    with patch("services.redsl_client.RedslClient", return_value=mock_redsl), \
         patch("worker.tasks.quality_loop._save_health_snapshot"), \
         patch("worker.tasks.quality_loop._check_health_drop"), \
         patch("worker.tasks.quality_loop._create_quality_ticket", return_value="ticket-456"), \
         patch("worker.tasks.quality_loop._update_ticket_status") as mock_update:
        result = await _run_quality_loop("org/repo", "abc123", "/tmp/repo", "", "github")
        assert result["status"] == "no_changes"
        mock_update.assert_called_once_with("ticket-456", "no_changes")


# ─── Helper unit tests ──────────────────────────────────────────────────────

def test_save_health_snapshot_catches_errors():
    from worker.tasks.quality_loop import _save_health_snapshot
    # Should not raise even when db_module is broken
    with patch("db_module.wrappers.save_scan", side_effect=Exception("db error")):
        _save_health_snapshot("org/repo", {"score": 80, "grade": "A"}, "abc123")


def test_check_health_drop_no_previous_data():
    from worker.tasks.quality_loop import _check_health_drop
    with patch("db_module.wrappers.get_repo_scans", return_value=[]):
        # Should not raise
        _check_health_drop("org/repo", 80)


def test_update_badge_cache_updates_store():
    from worker.tasks.quality_loop import _update_badge_cache
    import store

    _update_badge_cache("org/test", {"score": 92, "grade": "A+"})
    assert store.badge_cache["org/test"]["score"] == 92
    assert store.badge_cache["org/test"]["grade"] == "A+"
    # Cleanup
    del store.badge_cache["org/test"]
