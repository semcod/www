"""Unit tests for metrics API."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from server import app


client = TestClient(app)


def test_metrics_standard_endpoint():
    """Test the standard metrics endpoint."""
    response = client.get("/api/metrics/standard?limit=5")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "meta" in data
    assert "scans" in data
    assert "generated_at" in data["meta"]
    assert "total_scans" in data["meta"]
    assert "returned_scans" in data["meta"]
    assert isinstance(data["scans"], list)


def test_metrics_summary_endpoint():
    """Test the summary metrics endpoint."""
    response = client.get("/api/metrics/summary")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "meta" in data
    assert "summary" in data
    assert "avg_health_score" in data["summary"]
    assert "grade_distribution" in data["summary"]
    assert "platform_distribution" in data["summary"]


def test_metrics_repository_endpoint_not_found():
    """Test repository metrics endpoint with non-existent repo."""
    response = client.get("/api/metrics/repository/nonexistent/fake-repo")
    
    assert response.status_code == 404


def test_scans_recent_endpoint():
    """Test the recent scans endpoint."""
    response = client.get("/api/scans/recent?limit=10")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "scans" in data
    assert "total" in data
    assert isinstance(data["scans"], list)
    assert isinstance(data["total"], int)


def test_metrics_standard_limit_parameter():
    """Test that limit parameter works correctly."""
    response = client.get("/api/metrics/standard?limit=3")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["meta"]["returned_scans"] <= 3


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
