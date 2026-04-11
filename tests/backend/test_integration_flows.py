"""Integration flow tests — multi-step scenarios exercising real endpoint chains.

Each test class represents one end-to-end user journey that crosses
several routers/services and validates response content along the way.
"""
import time
import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.fast, pytest.mark.unit]

_TS = str(int(time.time() * 1000))[-6:]


# ── helpers ──────────────────────────────────────────────────────────────────

DEMO_USER = {"id": 1, "login": "demo-user", "name": "Demo User",
             "avatar_url": "", "github_token": ""}


def _override_auth(fastapi_app, user=DEMO_USER):
    from routers.auth import get_current_user
    fastapi_app.dependency_overrides[get_current_user] = lambda: user


def _clear_auth(fastapi_app):
    fastapi_app.dependency_overrides.clear()


# ── Flow 1: Auth → Repos → Audit → Trend → Badge ───────────────────────────

class TestAuditLifecycle:
    """Full user journey: login ➜ list repos ➜ start audit ➜ check trend ➜ fetch badge."""

    def test_demo_login_with_override(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.get("/api/me")
            assert resp.status_code == 200
            assert resp.json()["login"] == "demo-user"
        finally:
            _clear_auth(app)

    def test_list_repos_returns_demo_repos(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.get("/api/repos")
            assert resp.status_code == 200
            repos = resp.json()
            assert isinstance(repos, list)
            assert len(repos) >= 1
            names = [r["full_name"] for r in repos]
            assert "acme/backend-api" in names
        finally:
            _clear_auth(app)

    def test_audit_returns_valid_result(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.post("/api/audit", json={"repo": "acme/backend-api"})
            assert resp.status_code == 200
            data = resp.json()
            assert "audit_id" in data
            assert isinstance(data["audit_id"], str)
            assert len(data["audit_id"]) > 0
        finally:
            _clear_auth(app)

    def test_trend_endpoint(self, client):
        scan = {
            "repo": "acme/backend-api", "health_score": 75, "grade": "B",
            "stats": {"total_files": 10, "total_lines": 500,
                      "complexity": {"cc_avg": 3.0, "functions": 20},
                      "duplication": {"duplication_groups": 1, "recoverable_lines": 5},
                      "quality": {"passed": 18, "warnings": 1, "errors": 0}},
            "completed": "2026-04-10T10:00:00+00:00", "sandbox": False, "badge_url": "",
        }
        with patch("routers.trend.get_repo_scans", return_value=[scan]):
            resp = client.get("/api/trend/acme/backend-api?days=365")
        assert resp.status_code == 200
        data = resp.json()
        assert "meta" in data
        assert "trend" in data
        assert "points" in data

    def test_badge_svg_content_type(self, client):
        resp = client.get("/badge/acme-backend-api.svg")
        assert resp.status_code == 200
        ct = resp.headers.get("content-type", "")
        assert "svg" in ct or "xml" in ct
        assert "<svg" in resp.text

    def test_scan_diff_structure(self, client):
        scan_a = {
            "repo": "acme/backend-api", "health_score": 70, "grade": "B",
            "stats": {"total_files": 10, "total_lines": 1000,
                      "complexity": {"cc_avg": 3.0, "functions": 50},
                      "duplication": {"duplication_groups": 2, "recoverable_lines": 20},
                      "quality": {"passed": 40, "warnings": 3, "errors": 1}},
            "completed": "2026-01-01T10:00:00+00:00", "sandbox": False, "badge_url": "",
        }
        scan_b = {**scan_a, "health_score": 60, "grade": "C",
                  "completed": "2026-04-10T10:00:00+00:00"}
        with patch("routers.trend.get_repo_scans", return_value=[scan_a, scan_b]):
            resp = client.get("/api/scan/diff/acme/backend-api")
        assert resp.status_code == 200
        data = resp.json()
        assert "meta" in data
        assert "delta" in data


# ── Flow 2: Marketplace Install → App Status → Uninstall ────────────────────

class TestMarketplaceFlow:
    """Marketplace: list apps ➜ install ➜ check status ➜ uninstall ➜ verify removed."""

    def test_apps_list_has_required_shape(self, client):
        resp = client.get("/api/apps")
        assert resp.status_code == 200
        apps = resp.json()
        assert isinstance(apps, list)
        assert len(apps) >= 3
        for app in apps:
            assert "name" in app
            assert "version" in app
            assert "pricing" in app
            assert "triggers" in app
            assert "actions" in app

    def test_install_check_uninstall(self, client):
        from server import app as fastapi_app
        user = {"id": 1, "login": "flow-tester", "name": "FT",
                "avatar_url": "", "github_token": "ghp_test"}
        _override_auth(fastapi_app, user)
        try:
            repo = f"flow-test/repo-{_TS}"

            # Install
            install_resp = client.post("/api/install", json={
                "repo": repo, "provider": "github", "apps": ["audit", "security"],
            })
            assert install_resp.status_code == 200
            assert install_resp.json()["status"] == "installed"

            # Status should show installed
            status_resp = client.get(f"/api/apps/status?repo={repo}&provider=github")
            assert status_resp.status_code == 200
            assert status_resp.json()["installed"] is True
            assert "audit" in status_resp.json()["apps"]

            # Uninstall
            uninstall_resp = client.delete(f"/api/install?repo={repo}&provider=github")
            assert uninstall_resp.status_code == 200
            assert uninstall_resp.json()["status"] == "uninstalled"

        finally:
            fastapi_app.dependency_overrides.clear()


# ── Flow 3: Benchmark lifecycle ─────────────────────────────────────────────

class TestBenchmarkLifecycle:
    """Benchmark: create case ➜ feedback ➜ decision ➜ event ➜ summary ➜ export."""

    def test_full_lifecycle(self, client):
        cid = f"BM-INT-{_TS}"

        # 1. Create case
        resp = client.post("/api/benchmark/cases", json={
            "case_id": cid, "repo": "int-test/repo",
            "source_type": "pr", "change_type": "refactor",
            "baseline_detected": True, "baseline_tools": ["eslint"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["case_id"] == cid
        assert data["source_type"] == "pr"

        # 2. Patch
        resp = client.patch(f"/api/benchmark/cases/{cid}",
                            json={"reviewer_verdict": "go", "pr_candidate": True})
        assert resp.status_code == 200
        assert resp.json()["reviewer_verdict"] == "go"

        # 3. Decision
        resp = client.post(f"/api/benchmark/cases/{cid}/decision",
                           json={"deployment_model_selected": "hybrid", "pr_candidate": True})
        assert resp.status_code == 200
        assert resp.json()["deployment_model_selected"] == "hybrid"

        # 4. Feedback on two recommendations
        for rec_id in ["rec-A", "rec-B"]:
            resp = client.post(
                f"/api/benchmark/cases/{cid}/recommendations/{rec_id}/feedback",
                json={"accepted": rec_id == "rec-A", "novelty_score": 2, "usefulness_score": 3,
                      "notes": f"feedback for {rec_id}"},
            )
            assert resp.status_code == 200

        # 5. Events
        for ename in ["result_viewed", "recommendation_expanded", "export_clicked"]:
            resp = client.post(f"/api/benchmark/cases/{cid}/events",
                               json={"event_name": ename, "audit_id": "int-audit-1"})
            assert resp.status_code == 201

        # 6. List events
        resp = client.get(f"/api/benchmark/cases/{cid}/events")
        assert resp.status_code == 200
        assert len(resp.json()["events"]) >= 3

        # 7. List feedback
        resp = client.get(f"/api/benchmark/cases/{cid}/recommendations/feedback")
        assert resp.status_code == 200
        assert len(resp.json()["feedback"]) >= 2

        # 8. Summary
        resp = client.get("/api/benchmark/summary")
        assert resp.status_code == 200
        summary = resp.json()
        assert summary["total_cases"] >= 1

        # 9. Export JSON
        resp = client.get("/api/benchmark/export.json")
        assert resp.status_code == 200
        export = resp.json()
        assert any(c["case_id"] == cid for c in export["cases"])

        # 10. Export CSV
        resp = client.get("/api/benchmark/export.csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert cid in resp.text


# ── Flow 4: MCP Tool Chain ──────────────────────────────────────────────────

class TestMCPFlow:
    """MCP: info ➜ list resources ➜ list tools ➜ invoke tool ➜ get status."""

    def test_mcp_info(self, client):
        resp = client.get("/mcp/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "version" in data

    def test_mcp_list_resources(self, client):
        resp = client.get("/mcp/resources")
        assert resp.status_code == 200
        resources = resp.json()
        assert isinstance(resources, list)
        for r in resources:
            assert "uri" in r
            assert "name" in r

    def test_mcp_list_tools(self, client):
        resp = client.get("/mcp/tools")
        assert resp.status_code == 200
        tools = resp.json()
        assert isinstance(tools, list)
        names = [t["name"] for t in tools]
        assert "analyze_public_repo" in names

    def test_mcp_invoke_and_status(self, client):
        resp = client.post("/mcp/tools/invoke", json={
            "name": "analyze_public_repo",
            "arguments": {"repo_url": "https://github.com/acme/backend-api"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "audit_id" in data

        # Check status of the audit
        audit_id = data["audit_id"]
        resp2 = client.post("/mcp/tools/invoke", json={
            "name": "get_scan_status",
            "arguments": {"audit_id": audit_id},
        })
        assert resp2.status_code == 200


# ── Flow 5: Error scenarios across routers ───────────────────────────────────

class TestCrossRouterErrors:
    """Validate consistent error handling across routers."""

    def test_401_without_auth(self, client):
        for path in ["/api/repos", "/api/me", "/api/billing/status"]:
            resp = client.get(path)
            assert resp.status_code == 401, f"{path} should require auth"

    def test_404_for_missing(self, client):
        resp = client.get("/api/this-does-not-exist")
        assert resp.status_code in (404, 405)

    def test_audit_missing_repo_returns_error(self, client):
        from server import app
        _override_auth(app)
        try:
            # Missing repo field — endpoint uses body["repo"] directly (KeyError)
            with pytest.raises(KeyError):
                client.post("/api/audit", json={"invalid": "x"})
        finally:
            _clear_auth(app)

    def test_benchmark_404_chain(self, client):
        fake = "NOPE-999"
        assert client.get(f"/api/benchmark/cases/{fake}").status_code == 404
        assert client.patch(f"/api/benchmark/cases/{fake}", json={"reviewer_verdict": "go"}).status_code == 404
        assert client.post(f"/api/benchmark/cases/{fake}/decision", json={"pr_candidate": True}).status_code == 404
        assert client.post(f"/api/benchmark/cases/{fake}/events", json={"event_name": "x"}).status_code == 404


# ── Flow 6: Billing ─────────────────────────────────────────────────────────

class TestBillingFlow:
    """Billing: list plans ➜ check status."""

    def test_plans_shape(self, client):
        resp = client.get("/api/billing/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert "free" in data
        assert "pro" in data

    def test_billing_status(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.get("/api/billing/status")
            assert resp.status_code == 200
            data = resp.json()
            assert "plan" in data
            assert "status" in data
            assert "scans_remaining" in data
        finally:
            _clear_auth(app)


# ── Flow 7: Content-Type validation ─────────────────────────────────────────

class TestContentTypes:
    """Verify every major endpoint returns correct Content-Type."""

    def test_json_endpoints_return_json(self, client):
        from server import app
        _override_auth(app)
        try:
            json_paths = [
                "/api/health",
                "/api/apps",
                "/api/repos",
                "/api/billing/plans",
                "/mcp/info",
                "/mcp/resources",
                "/mcp/tools",
                "/api/benchmark/summary",
                "/api/benchmark/export.json",
                "/api/scans/recent?limit=5",
            ]
            for path in json_paths:
                resp = client.get(path)
                ct = resp.headers.get("content-type", "")
                assert "json" in ct, f"{path} should return JSON, got {ct}"
        finally:
            _clear_auth(app)

    def test_csv_endpoint_returns_csv(self, client):
        resp = client.get("/api/benchmark/export.csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    def test_badge_returns_svg(self, client):
        resp = client.get("/badge/test-repo.svg")
        assert resp.status_code == 200
        ct = resp.headers.get("content-type", "")
        assert "svg" in ct or "xml" in ct


# ── Flow 8: Scheduler ───────────────────────────────────────────────────────

class TestSchedulerFlow:
    """Scheduler: list ➜ create ➜ list again."""

    def test_list_schedules(self, client):
        resp = client.get("/api/schedules")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_schedule(self, client):
        from server import app
        _override_auth(app)
        try:
            resp = client.post("/api/schedules", json={
                "repo": f"schedule-test/repo-{_TS}",
                "cron": "0 6 * * 1",
            })
            assert resp.status_code in (201, 409)  # 409 if already exists
        finally:
            _clear_auth(app)
