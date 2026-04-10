"""App registry - manages loaded apps and event routing."""
from typing import Dict, List, Optional, Any
from events.models import Event, EventType

from .base import AppBase, AppContext, AppResult
from .loader import load_apps, load_app


class AppRegistry:
    """Central registry for all marketplace apps.

    Handles:
    - Loading apps from apps/ directory
    - Event routing to appropriate apps
    - Result aggregation
    - App lifecycle management
    """

    def __init__(self):
        self._apps: Dict[str, Dict] = {}  # name -> {class, instance, manifest, pricing}
        self._initialized = False

    def initialize(self):
        """Load all apps from apps/ directory."""
        if self._initialized:
            return

        apps_data = load_apps()

        for name, data in apps_data.items():
            self._apps[name] = {
                "class": data["class"],
                "instance": None,  # Lazy initialization
                "manifest": data["manifest"],
                "pricing": data["pricing"],
            }

        self._initialized = True
        print(f"[registry] Loaded {len(self._apps)} apps: {list(self._apps.keys())}")

    def get_app(self, name: str) -> Optional[AppBase]:
        """Get app instance by name (lazy initialization)."""
        if name not in self._apps:
            return None

        app_data = self._apps[name]

        # Initialize instance if needed
        if app_data["instance"] is None:
            config = {
                **app_data["manifest"].get("config", {}),
                **app_data["pricing"],
            }
            app_data["instance"] = app_data["class"](config)

        return app_data["instance"]

    def get_apps_for_event(self, event: Event) -> List[tuple]:
        """Get all apps that should handle this event.

        Returns:
            List of (app_name, app_instance) tuples
        """
        if not self._initialized:
            self.initialize()

        matching = []
        event_type = self._event_to_trigger(event.type)

        for name, data in self._apps.items():
            triggers = data["manifest"].get("triggers", [])
            if event_type in triggers:
                app = self.get_app(name)
                if app:
                    matching.append((name, app))

        return matching

    def process_event(self, event: Event) -> Dict[str, AppResult]:
        """Route event to all matching apps and collect results.

        Args:
            event: Unified event object

        Returns:
            Dict mapping app_name -> AppResult
        """
        results = {}
        apps = self.get_apps_for_event(event)

        # Build context
        context = AppContext(
            repo=event.repo,
            event_type=event.type.value,
            provider=event.provider.value,
            pr_id=event.pr_id,
            branch=event.branch,
            base_branch=event.base_branch,
            diff=event.diff,
            commit_sha=event.commit_sha,
            author=event.author,
            raw_event=event.raw_payload,
        )

        for name, app in apps:
            # Check if app can execute
            if not app.can_execute(context):
                results[name] = AppResult(
                    status="skipped",
                    details={"reason": "not enabled for this repo or billing"},
                )
                continue

            # Route to specific handler based on action
            try:
                if event.type == EventType.PULL_REQUEST:
                    if event.action == "opened":
                        result = app.on_pr_opened(context)
                    elif event.action == "synchronize":
                        result = app.on_pr_synchronize(context)
                    else:
                        result = AppResult(status="skipped", details={"reason": "unhandled action"})
                elif event.type == EventType.PUSH:
                    result = app.on_push(context)
                else:
                    result = app.run_pipeline(context)

                results[name] = result

            except Exception as e:
                results[name] = AppResult(
                    status="error",
                    details={"error": str(e)},
                )

        return results

    def list_apps(self) -> List[Dict]:
        """List all registered apps with metadata."""
        if not self._initialized:
            self.initialize()

        return [
            {
                "name": name,
                "version": data["manifest"].get("version", "0.0.0"),
                "description": data["manifest"].get("description", ""),
                "triggers": data["manifest"].get("triggers", []),
                "actions": data["manifest"].get("actions", []),
                "pricing": data["pricing"].get("tier", "free"),
                "enabled": data["instance"] is not None if data["instance"] else True,
            }
            for name, data in self._apps.items()
        ]

    def get_app_manifest(self, name: str) -> Optional[Dict]:
        """Get manifest for specific app."""
        if name not in self._apps:
            return None
        return self._apps[name]["manifest"]

    @staticmethod
    def _event_to_trigger(event_type: EventType) -> str:
        """Convert EventType to trigger string used in manifests."""
        mapping = {
            EventType.PULL_REQUEST: "pull_request",
            EventType.PUSH: "push",
            EventType.ISSUE: "issue",
            EventType.PULL_REQUEST_COMMENT: "pull_request_comment",
        }
        return mapping.get(event_type, "unknown")


# Global registry instance
_registry: Optional[AppRegistry] = None


def get_registry() -> AppRegistry:
    """Get singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = AppRegistry()
    return _registry
