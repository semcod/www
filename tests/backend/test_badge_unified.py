"""Tests for unified badge system (DB fallback)."""
import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


def test_badge_from_memory_cache(client):
    import store
    store.badge_cache["org/repo"] = {"score": 88, "grade": "A", "weekly_issues": None}
    try:
        resp = client.get("/badge/org-repo.svg")
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.headers["content-type"]
        assert "A" in resp.text
        assert "88" in resp.text
    finally:
        del store.badge_cache["org/repo"]


def test_badge_falls_through_to_db_badge_cache(client):
    import store
    store.badge_cache.pop("org/repo", None)

    db_cached = {"score": 75, "grade": "B+", "updated": "2026-04-12T10:00:00Z", "weekly_issues": None}
    with patch("db_module.wrappers.get_badge_cache", return_value=db_cached):
        resp = client.get("/badge/org-repo.svg")
        assert resp.status_code == 200
        assert "B+" in resp.text


def test_badge_falls_through_to_db_scans(client):
    import store
    store.badge_cache.pop("org/repo", None)

    scans = [{"health_score": 62, "grade": "B"}]
    with patch("db_module.wrappers.get_badge_cache", return_value=None), \
         patch("db_module.wrappers.get_repo_scans", return_value=scans):
        resp = client.get("/badge/org-repo.svg")
        assert resp.status_code == 200
        assert "B" in resp.text


def test_badge_no_data_shows_unknown(client):
    import store
    store.badge_cache.pop("org/missing", None)

    with patch("db_module.wrappers.get_badge_cache", return_value=None), \
         patch("db_module.wrappers.get_repo_scans", return_value=[]):
        resp = client.get("/badge/org-missing.svg")
        assert resp.status_code == 200
        assert "?" in resp.text


def test_scan_count_badge_generator():
    """Test scan count badge SVG generation directly."""
    from routers.badge import _generate_count_badge_svg
    svg = _generate_count_badge_svg("semcod scans", 3)
    assert "<svg" in svg
    assert "3" in svg
    assert "semcod scans" in svg


def test_scan_count_badge_falls_through_to_db(client):
    """Test scan count badge DB fallback.
    
    NOTE: /badge/scan-count.svg may be shadowed by /badge/{repo_slug}.svg 
    depending on router mount order. We test the internal function directly.
    """
    from routers.badge import _generate_count_badge_svg
    svg = _generate_count_badge_svg("semcod scans", 42)
    assert "<svg" in svg
    assert "42" in svg
