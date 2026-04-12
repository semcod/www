"""Tests for system API endpoints."""

import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestHealthCheck:
    """Tests for /api/health endpoint."""

    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "tools" in data
        assert "timestamp" in data

    def test_health_check_tools(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        tools = data["tools"]
        assert isinstance(tools, list)
        assert "code2llm" in tools
        assert "redup" in tools
        assert "pyqual" in tools

    def test_health_check_cache_stats(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert "audits_cached" in data
        assert "badges_cached" in data
        assert isinstance(data["audits_cached"], int)
        assert isinstance(data["badges_cached"], int)


class TestDomainConfig:
    """Tests for /api/config/domain endpoint."""

    def test_domain_config(self, client):
        resp = client.get("/api/config/domain")
        assert resp.status_code == 200
        data = resp.json()
        assert "domain" in data
        assert isinstance(data["domain"], str)

    @patch("config.PUBLIC_URL", "https://semcod.com")
    def test_domain_strips_protocol(self, client):
        resp = client.get("/api/config/domain")
        data = resp.json()
        assert data["domain"] == "semcod.com"

    @patch("config.PUBLIC_URL", "http://localhost:8003")
    def test_domain_localhost_fallback(self, client):
        resp = client.get("/api/config/domain")
        data = resp.json()
        assert data["domain"] == "semcod.com"
