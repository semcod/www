"""Tests for badge API endpoints."""

import pytest

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestHealthBadge:
    """Tests for /badge/{repo_slug}.svg endpoint."""

    def test_badge_without_cache(self, client):
        """Badge returns SVG with '?' grade when no cached data."""
        resp = client.get("/badge/unknown-repo.svg")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/svg+xml"
        svg = resp.text
        assert "<svg" in svg
        assert "?" in svg

    def test_badge_with_cache(self, client):
        """Badge returns SVG with cached grade when data exists."""
        from store import badge_cache
        badge_cache.pop("owner/repo", None)  # Clear stale state
        badge_cache["owner/repo"] = {
            "score": 85,
            "grade": "A",
            "weekly_issues": None,
            "updated": "2026-01-01T00:00:00",
        }
        try:
            resp = client.get("/badge/owner-repo.svg")
            assert resp.status_code == 200
            svg = resp.text
            assert "A" in svg
            assert "85" in svg
        finally:
            badge_cache.pop("owner/repo", None)

    def test_badge_with_weekly_issues(self, client):
        """Badge shows 'issues prevented' when weekly_issues > 0."""
        from store import badge_cache
        badge_cache["acme/app"] = {
            "score": 70,
            "grade": "B",
            "weekly_issues": 3,
            "updated": "2026-01-01T00:00:00",
        }
        try:
            resp = client.get("/badge/acme-app.svg")
            assert resp.status_code == 200
            svg = resp.text
            assert "3 issues prevented" in svg
        finally:
            badge_cache.pop("acme/app", None)

    def test_badge_has_no_cache_headers(self, client):
        """Badge response has no-cache headers."""
        resp = client.get("/badge/test-repo.svg")
        assert resp.status_code == 200
        assert "no-cache" in resp.headers.get("cache-control", "")

    def test_badge_etag_header(self, client):
        """Badge response includes ETag header."""
        resp = client.get("/badge/test-repo.svg")
        assert resp.status_code == 200
        assert "etag" in resp.headers


class TestScanCountBadge:
    """Tests for scan count badge SVG generation."""

    def test_scan_count_badge_svg_generation(self):
        """Test internal SVG generation for scan count badge."""
        from routers.badge import _generate_count_badge_svg
        svg = _generate_count_badge_svg("semcod scans", 42)
        assert "<svg" in svg
        assert "42" in svg
        assert "semcod scans" in svg

    def test_scan_count_badge_endpoint(self, client):
        """Test scan count badge endpoint returns valid SVG."""
        resp = client.get("/badge/scan-count.svg")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/svg+xml"
        assert "<svg" in resp.text


class TestBadgeSvgGeneration:
    """Tests for internal SVG generation function."""

    def test_generate_badge_svg_grade_a_plus(self):
        from routers.badge import _generate_badge_svg
        svg = _generate_badge_svg("A+", 95, "flat")
        assert "#22c55e" in svg  # green color for A+

    def test_generate_badge_svg_grade_f(self):
        from routers.badge import _generate_badge_svg
        svg = _generate_badge_svg("F", 20, "flat")
        assert "#ef4444" in svg  # red color for F

    def test_generate_badge_svg_unknown_grade(self):
        from routers.badge import _generate_badge_svg
        svg = _generate_badge_svg("?", None, "flat")
        assert "#94a3b8" in svg  # gray color for unknown

    def test_generate_count_badge_svg(self):
        from routers.badge import _generate_count_badge_svg
        svg = _generate_count_badge_svg("test label", 42)
        assert "42" in svg
        assert "test label" in svg
