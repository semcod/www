"""Tests for report API endpoint."""

import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestReportRedirect:
    """Tests for /report/{owner}/{repo} endpoint."""

    @patch("routers.report.FRONTEND_URL", "http://localhost:3000")
    def test_report_redirect(self, client):
        resp = client.get("/report/acme/backend-api", follow_redirects=False)
        assert resp.status_code == 307
        location = resp.headers.get("location", "")
        assert "localhost:3000" in location
        assert "acme" in location
        assert "backend-api" in location

    @patch("routers.report.FRONTEND_URL", "http://localhost:3000")
    def test_report_redirect_format(self, client):
        resp = client.get("/report/owner/repo", follow_redirects=False)
        location = resp.headers.get("location", "")
        assert location == "http://localhost:3000/report/owner/repo"
