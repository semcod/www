from fastapi.testclient import TestClient

from server import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert isinstance(data["audits_cached"], int)
    assert isinstance(data["badges_cached"], int)


def test_core_routes_are_registered():
    routes = {
        (route.path, tuple(sorted(route.methods)))
        for route in app.routes
        if hasattr(route, "methods")
    }

    assert ("/api/health", ("GET",)) in routes
    assert ("/auth/github", ("GET",)) in routes
    assert ("/auth/callback", ("GET",)) in routes
    assert ("/api/repos", ("GET",)) in routes
    assert ("/api/audit", ("POST",)) in routes
    assert ("/api/audit/{audit_id}", ("GET",)) in routes
    assert ("/api/analyze", ("POST",)) in routes
    assert ("/webhook/github", ("POST",)) in routes
    assert ("/badge/{repo_slug}.svg", ("GET",)) in routes
    assert ("/report/{owner}/{repo}", ("GET",)) in routes
