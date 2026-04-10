"""Pytest configuration and fixtures for faster testing."""

import pytest
from fastapi.testclient import TestClient


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """Reusable TestClient for the FastAPI app (session-scoped for speed)."""
    from server import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def mock_asyncio_create_task(monkeypatch):
    """Auto-mock asyncio.create_task to prevent hanging background tasks."""
    import asyncio
    original_create_task = asyncio.create_task
    
    def mock_create_task(coro, *, name=None, context=None):
        # Don't actually run the coroutine, just return a mock task
        class MockTask:
            def cancel(self):
                pass
            def cancelled(self):
                return False
            def done(self):
                return True
            def result(self):
                return None
        return MockTask()
    
    monkeypatch.setattr(asyncio, "create_task", mock_create_task)
    yield


# ─── Pytest Hooks for Performance ────────────────────────────────────────────

def pytest_configure(config):
    """Configure pytest for optimal performance."""
    # Disable warnings that slow down test collection
    config.option.strict_markers = True


def pytest_collection_modifyitems(config, items):
    """Modify test items for better performance."""
    # Auto-add 'unit' marker to tests without any marker
    for item in items:
        if not any(marker.name in ["fast", "slow", "integration", "unit"] 
                   for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# ─── Performance Markers ───────────────────────────────────────────────────

def pytest_runtest_setup(item):
    """Setup hook to skip slow tests in fast mode."""
    # Check if --fast flag is passed via -m fast
    markers = [m.name for m in item.iter_markers()]
    
    # If running with -m fast, skip slow/integration tests
    if item.config.getoption("-m") == "fast":
        if "slow" in markers or "integration" in markers:
            pytest.skip("Skipping slow/integration test in fast mode")
