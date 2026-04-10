"""MCP (Model Context Protocol) endpoint tests."""

import pytest

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestMCPResources:
    """Test MCP resource discovery and content."""
    
    def test_list_resources(self, client):
        """Test MCP resources listing."""
        response = client.get("/mcp/resources")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4
        
        uris = [r["uri"] for r in data]
        assert "scans://list" in uris
        assert "scan://{audit_id}" in uris
        assert "metrics://summary" in uris
        assert "badge://{repo_slug}" in uris
    
    def test_get_scans_list_resource(self, client):
        """Test getting scans list resource."""
        response = client.get("/mcp/resources/content?uri=scans://list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uri"] == "scans://list"
        assert "scans" in data["content"]
        assert "total_available" in data["content"]
    
    def test_get_metrics_summary_resource(self, client):
        """Test getting metrics summary resource."""
        response = client.get("/mcp/resources/content?uri=metrics://summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uri"] == "metrics://summary"
        assert "meta" in data["content"]
        assert "summary" in data["content"]
        assert "avg_health_score" in data["content"]["summary"]
    
    def test_get_badge_resource(self, client):
        """Test getting badge resource."""
        response = client.get("/mcp/resources/content?uri=badge://owner-repo")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uri"] == "badge://owner-repo"
        assert data["content"]["repository"] == "owner/repo"
    
    def test_get_unknown_resource_returns_404(self, client):
        """Test unknown resource returns 404."""
        response = client.get("/mcp/resources/content?uri=unknown://test")
        assert response.status_code == 404


class TestMCPTools:
    """Test MCP tool discovery and invocation."""
    
    def test_list_tools(self, client):
        """Test MCP tools listing."""
        response = client.get("/mcp/tools")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        names = [t["name"] for t in data]
        assert "start_audit" in names
        assert "get_scan_status" in names
        assert "get_repository_metrics" in names
        assert "analyze_public_repo" in names
    
    def test_tool_start_audit(self, client, monkeypatch):
        """Test start_audit tool."""
        response = client.post("/mcp/invoke", json={
            "name": "start_audit",
            "arguments": {"repo": "test-owner/test-repo", "token": "fake-token"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "audit_id" in data
        assert data["status"] == "running"
        assert len(data["audit_id"]) == 12
    
    def test_tool_get_scan_status(self, client):
        """Test get_scan_status tool."""
        # First create a scan
        client.post("/mcp/invoke", json={
            "name": "start_audit",
            "arguments": {"repo": "test/repo"}
        })
        
        # Get list to find the audit_id
        scans_response = client.get("/mcp/resources/content?uri=scans://list")
        scans = scans_response.json()["content"]["scans"]
        
        if scans:
            audit_id = scans[0]["audit_id"]
            response = client.post("/mcp/invoke", json={
                "name": "get_scan_status",
                "arguments": {"audit_id": audit_id}
            })
            assert response.status_code == 200
            assert response.json()["audit_id"] == audit_id
    
    def test_tool_get_scan_status_not_found(self, client):
        """Test get_scan_status for non-existent scan."""
        response = client.post("/mcp/invoke", json={
            "name": "get_scan_status",
            "arguments": {"audit_id": "nonexistent123"}
        })
        assert response.status_code == 404
    
    def test_tool_analyze_public_repo(self, client, monkeypatch):
        """Test analyze_public_repo tool."""
        response = client.post("/mcp/invoke", json={
            "name": "analyze_public_repo",
            "arguments": {"repo_url": "https://github.com/facebook/react"}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "audit_id" in data
        assert data["status"] == "running"
        assert "repo" in data
    
    def test_tool_analyze_public_repo_invalid_url(self, client):
        """Test analyze_public_repo with invalid URL."""
        response = client.post("/mcp/invoke", json={
            "name": "analyze_public_repo",
            "arguments": {"repo_url": "not-a-valid-url"}
        })
        assert response.status_code == 400
    
    def test_unknown_tool_returns_400(self, client):
        """Test unknown tool returns 400."""
        response = client.post("/mcp/invoke", json={
            "name": "unknown_tool",
            "arguments": {}
        })
        assert response.status_code == 400


class TestMCPInfo:
    """Test MCP server info endpoint."""
    
    def test_mcp_server_info(self, client):
        """Test MCP server info."""
        response = client.get("/mcp/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "semcod-mcp"
        assert "version" in data
        assert "protocol_version" in data
        assert "resources" in data
        assert "tools" in data
