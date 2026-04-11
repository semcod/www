"""ReDSL router and client tests."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_httpx_context(mock_resp=None, side_effect=None):
    """Build a mock httpx.AsyncClient context manager."""
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    if side_effect:
        mock_ctx.get = AsyncMock(side_effect=side_effect)
        mock_ctx.post = AsyncMock(side_effect=side_effect)
    elif mock_resp:
        mock_ctx.get = AsyncMock(return_value=mock_resp)
        mock_ctx.post = AsyncMock(return_value=mock_resp)
    return mock_ctx


# ─── RedslClient tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_redsl_client_health_score():
    from services.redsl_client import RedslClient
    client = RedslClient("http://localhost:9999")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"score": 72.5, "grade": "B+", "cc_mean": 3.1}
    mock_resp.raise_for_status = MagicMock()

    with patch("services.redsl_client.httpx.AsyncClient", return_value=_mock_httpx_context(mock_resp)):
        result = await client.health_score("/tmp/test-repo")
        assert result["score"] == 72.5
        assert result["grade"] == "B+"


@pytest.mark.asyncio
async def test_redsl_client_health_unavailable():
    import httpx as _httpx
    from services.redsl_client import RedslClient
    client = RedslClient("http://localhost:19999")

    with patch("services.redsl_client.httpx.AsyncClient", return_value=_mock_httpx_context(side_effect=_httpx.ConnectError("refused"))):
        result = await client.health()
        assert result is False


# ─── Router tests ─────────────────────────────────────────────────────────────

def test_redsl_status_endpoint(client):
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=True):
        resp = client.get("/api/redsl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True


def test_redsl_status_unavailable(client):
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=False):
        resp = client.get("/api/redsl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is False


def test_redsl_analyze_unavailable(client):
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=False):
        resp = client.post("/api/redsl/analyze", json={"project_path": "/tmp/test"})
        assert resp.status_code == 503


def test_redsl_analyze_success(client):
    mock_result = {"cc_mean": 3.0, "critical": 0, "god_modules": 0}
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=True), \
         patch("services.redsl_client.RedslClient.analyze", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post("/api/redsl/analyze", json={"project_path": "/tmp/test"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "analyzed"
        assert data["result"]["cc_mean"] == 3.0


def test_redsl_health_endpoint(client):
    mock_health = {"score": 85, "grade": "A", "cc_mean": 2.7, "critical": 0, "god_modules": 0, "max_cc": 13}
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=True), \
         patch("services.redsl_client.RedslClient.health_score", new_callable=AsyncMock, return_value=mock_health):
        resp = client.post("/api/redsl/health", json={"project_path": "/tmp/test"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 85
        assert data["grade"] == "A"


def test_redsl_refactor_preview(client):
    mock_result = {"decisions": [{"action": "EXTRACT_FUNCTIONS", "target_file": "a.py", "score": 8.5}]}
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=True), \
         patch("services.redsl_client.RedslClient.refactor", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post("/api/redsl/refactor", json={"project_path": "/tmp/test", "dry_run": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "preview"


def test_redsl_decide_endpoint(client):
    mock_decisions = [{"action": "SPLIT_MODULE", "target": "big.py", "reason": "CC=22"}]
    with patch("services.redsl_client.RedslClient.health", new_callable=AsyncMock, return_value=True), \
         patch("services.redsl_client.RedslClient.decide", new_callable=AsyncMock, return_value=mock_decisions):
        resp = client.post("/api/redsl/decide", json={"project_path": "/tmp/test"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["decisions"]) == 1


def test_redsl_badge_endpoint(client):
    with patch("services.scan_service.get_repo_scans", return_value=[{"health_score": 85}]):
        resp = client.get("/api/redsl/badge/owner/repo")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/svg+xml"
        assert "A" in resp.text


def test_redsl_badge_no_scans(client):
    with patch("services.scan_service.get_repo_scans", return_value=[]):
        resp = client.get("/api/redsl/badge/owner/repo")
        assert resp.status_code == 200
        assert "?" in resp.text


# ─── Badge helper tests ───────────────────────────────────────────────────────

def test_score_to_grade():
    from routers.redsl import _score_to_grade
    assert _score_to_grade(97) == "A+"
    assert _score_to_grade(85) == "A"
    assert _score_to_grade(75) == "B+"
    assert _score_to_grade(65) == "B"
    assert _score_to_grade(50) == "C"
    assert _score_to_grade(35) == "D"
    assert _score_to_grade(20) == "F"


def test_make_badge_svg():
    from routers.redsl import _make_badge_svg
    svg = _make_badge_svg("code health", "A (85)", "green")
    assert "<svg" in svg
    assert "code health" in svg
    assert "A (85)" in svg
