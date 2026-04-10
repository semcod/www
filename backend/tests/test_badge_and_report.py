from fastapi.testclient import TestClient

from server import app
from store import badge_cache


client = TestClient(app)


def setup_function():
    badge_cache.clear()


def test_badge_returns_default_svg_for_unknown_repo():
    response = client.get("/badge/acme-repo.svg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert response.headers["etag"] == '"?-None"'
    assert "code health" in response.text
    assert "?" in response.text


def test_badge_returns_cached_score_and_grade():
    badge_cache["acme/repo"] = {
        "score": 91,
        "grade": "A+",
        "updated": "2026-04-10T00:00:00",
        "weekly_issues": 0,
    }

    response = client.get("/badge/acme-repo.svg")

    assert response.status_code == 200
    assert response.headers["etag"] == '"A+-91"'
    assert "AI review" in response.text
    assert "active" in response.text


def test_report_redirects_to_frontend_route():
    response = client.get("/report/acme/repo", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"].endswith("/report/acme/repo")
