"""Tests for marketplace app system (loader, registry, apps)."""

import pytest
from unittest.mock import patch, MagicMock

from apps.base import AppBase, AppContext, AppResult
from apps.loader import load_apps, load_manifest, validate_manifest
from apps.registry import AppRegistry, get_registry
from events.models import Event, EventType, ProviderType

pytestmark = [pytest.mark.fast, pytest.mark.unit]


# ─── Test App Implementation ────────────────────────────────────────────────────


class TestApp(AppBase):
    """Simple test app for unit tests."""

    def run_pipeline(self, context: AppContext) -> AppResult:
        return AppResult(
            status="success",
            score=85,
            issues=[],
            metrics={"test": True},
        )


# ─── Manifest Tests ────────────────────────────────────────────────────────────────


class TestManifestValidation:
    def test_valid_manifest(self):
        manifest = {
            "name": "test-app",
            "version": "1.0.0",
            "triggers": ["pull_request"],
            "actions": ["comment"],
        }
        errors = validate_manifest(manifest)
        assert errors == []

    def test_missing_required_fields(self):
        manifest = {"name": "test"}
        errors = validate_manifest(manifest)
        assert len(errors) == 3  # version, triggers, actions
        assert any("version" in e for e in errors)

    def test_invalid_trigger(self):
        manifest = {
            "name": "test",
            "version": "1.0.0",
            "triggers": ["invalid_trigger"],
            "actions": ["comment"],
        }
        errors = validate_manifest(manifest)
        assert any("Invalid trigger" in e for e in errors)


class TestLoadManifest:
    def test_load_audit_manifest(self):
        manifest = load_manifest("audit")
        assert manifest is not None
        assert manifest["name"] == "audit"
        assert "triggers" in manifest

    def test_load_security_manifest(self):
        manifest = load_manifest("security")
        assert manifest is not None
        assert manifest["name"] == "security"

    def test_load_nonexistent(self):
        manifest = load_manifest("nonexistent")
        assert manifest is None


class TestLoadApps:
    def test_loads_builtin_apps(self):
        apps = load_apps()
        assert "audit" in apps
        assert "security" in apps
        assert "performance" in apps

    def test_app_has_required_keys(self):
        apps = load_apps()
        for name, data in apps.items():
            assert "class" in data
            assert "manifest" in data
            assert "pricing" in data
            assert issubclass(data["class"], AppBase)


# ─── App Base Tests ──────────────────────────────────────────────────────────────


class TestAppBase:
    def test_app_result_defaults(self):
        result = AppResult(status="success")
        assert result.issues == []
        assert result.recommendations == []
        assert result.metrics == {}

    def test_app_context_defaults(self):
        ctx = AppContext(repo="owner/repo", event_type="pull_request", provider="github")
        assert ctx.config == {}
        assert ctx.raw_event == {}

    def test_app_can_execute_no_restrictions(self):
        app = TestApp({})
        ctx = AppContext(repo="owner/repo", event_type="pr", provider="github")
        assert app.can_execute(ctx) is True

    def test_app_can_execute_with_repo_filter(self):
        app = TestApp({"enabled_repos": ["owner/repo"]})

        ctx_allowed = AppContext(repo="owner/repo", event_type="pr", provider="github")
        assert app.can_execute(ctx_allowed) is True

        ctx_blocked = AppContext(repo="other/repo", event_type="pr", provider="github")
        assert app.can_execute(ctx_blocked) is False

    def test_pricing_tier_default(self):
        app = TestApp({})
        assert app.get_pricing_tier() == "free"

    def test_pricing_tier_configured(self):
        app = TestApp({"pricing": "pro"})
        assert app.get_pricing_tier() == "pro"


# ─── Registry Tests ──────────────────────────────────────────────────────────────


class TestAppRegistry:
    @pytest.fixture
    def registry(self):
        reg = AppRegistry()
        reg.initialize()
        return reg

    def test_initialize_loads_apps(self, registry):
        apps = registry.list_apps()
        assert len(apps) >= 3
        names = [a["name"] for a in apps]
        assert "audit" in names

    def test_get_app_returns_instance(self, registry):
        app = registry.get_app("audit")
        assert app is not None
        assert isinstance(app, AppBase)

    def test_get_app_caches_instance(self, registry):
        app1 = registry.get_app("audit")
        app2 = registry.get_app("audit")
        assert app1 is app2  # Same instance

    def test_get_app_invalid_returns_none(self, registry):
        app = registry.get_app("nonexistent")
        assert app is None

    def test_process_event_routes_to_apps(self, registry):
        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            action="opened",
            pr_id=1,
            raw_payload={},
        )

        results = registry.process_event(event)

        # Should have results from matching apps
        assert "audit" in results
        assert isinstance(results["audit"], AppResult)

    def test_list_apps_structure(self, registry):
        apps = registry.list_apps()
        for app in apps:
            assert "name" in app
            assert "version" in app
            assert "triggers" in app
            assert "actions" in app
            assert "pricing" in app


class TestRegistrySingleton:
    def test_singleton_pattern(self):
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2


# ─── Integration Tests ───────────────────────────────────────────────────────────


class TestAppIntegration:
    def test_audit_app_pipeline(self):
        from apps.audit.pipeline import AuditApp

        app = AuditApp()
        ctx = AppContext(
            repo="owner/repo",
            event_type="pull_request",
            provider="github",
            diff="def complex_function():\n    if a: ...\n    # TODO: refactor",
        )

        result = app.run_pipeline(ctx)

        assert isinstance(result, AppResult)
        assert result.status in ["success", "warning", "error"]
        assert result.score is not None
        assert 0 <= result.score <= 100

    def test_security_app_pipeline(self):
        from apps.security.pipeline import SecurityApp

        app = SecurityApp()
        ctx = AppContext(
            repo="owner/repo",
            event_type="pull_request",
            provider="github",
            diff="API_KEY = 'sk-test123'\neval(user_input)",
        )

        result = app.run_pipeline(ctx)

        assert isinstance(result, AppResult)
        assert any(i["type"] == "secret" for i in result.issues)
        assert any(i["type"] == "code_injection" for i in result.issues)

    def test_performance_app_pipeline(self):
        from apps.performance.pipeline import PerformanceApp

        app = PerformanceApp()
        ctx = AppContext(
            repo="owner/repo",
            event_type="pull_request",
            provider="github",
            diff="items.forEach(async (item) => await process(item))",
        )

        result = app.run_pipeline(ctx)

        assert isinstance(result, AppResult)
        assert result.status in ["success", "warning"]


# ─── Event Routing Tests ───────────────────────────────────────────────────────────


class TestEventRouting:
    def test_pr_event_matches_pr_apps(self):
        from apps.registry import AppRegistry

        registry = AppRegistry()
        registry.initialize()

        event = Event(
            type=EventType.PULL_REQUEST,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            action="opened",
        )

        apps = registry.get_apps_for_event(event)
        assert len(apps) > 0

        # All returned apps should have pull_request trigger
        for name, app in apps:
            triggers = app.get_triggers()
            assert "pull_request" in triggers

    def test_push_event_matches_push_apps(self):
        from apps.registry import AppRegistry

        registry = AppRegistry()
        registry.initialize()

        event = Event(
            type=EventType.PUSH,
            provider=ProviderType.GITHUB,
            repo="owner/repo",
            branch="main",
            commits=[],
        )

        apps = registry.get_apps_for_event(event)
        # Should match apps with 'push' trigger
        for name, app in apps:
            assert "push" in app.get_triggers()
