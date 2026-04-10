"""App loader - dynamically loads marketplace plugins from apps/ directory."""
import json
import yaml
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import AppBase


APPS_DIR = Path(__file__).parent


def load_manifest(app_name: str) -> Optional[Dict]:
    """Load manifest.yaml for an app."""
    manifest_path = APPS_DIR / app_name / "manifest.yaml"
    if not manifest_path.exists():
        # Try JSON fallback
        manifest_path = APPS_DIR / app_name / "manifest.json"
        if not manifest_path.exists():
            return None

    with open(manifest_path) as f:
        if manifest_path.suffix == ".yaml":
            return yaml.safe_load(f)
        return json.load(f)


def load_pricing(app_name: str) -> Optional[Dict]:
    """Load pricing.json for an app."""
    pricing_path = APPS_DIR / app_name / "pricing.json"
    if not pricing_path.exists():
        return None

    with open(pricing_path) as f:
        return json.load(f)


def load_app(app_name: str) -> Optional[Type[AppBase]]:
    """Load a single app by name.

    Args:
        app_name: Name of the app directory

    Returns:
        App class or None if loading fails
    """
    # Check manifest exists
    manifest = load_manifest(app_name)
    if not manifest:
        return None

    # Load pipeline.py module
    pipeline_path = APPS_DIR / app_name / "pipeline.py"
    if not pipeline_path.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            f"apps.{app_name}.pipeline",
            pipeline_path,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find App class in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, AppBase)
                and attr is not AppBase
            ):
                return attr

        return None

    except Exception as e:
        print(f"[loader] Failed to load app {app_name}: {e}")
        return None


def load_apps() -> Dict[str, Dict]:
    """Load all available apps.

    Returns:
        Dict mapping app_name -> {"class": AppClass, "manifest": dict, "pricing": dict}
    """
    apps = {}

    for app_dir in APPS_DIR.iterdir():
        if not app_dir.is_dir() or app_dir.name.startswith("_"):
            continue

        manifest = load_manifest(app_dir.name)
        if not manifest:
            continue

        app_class = load_app(app_dir.name)
        if not app_class:
            continue

        pricing = load_pricing(app_dir.name)

        apps[app_dir.name] = {
            "class": app_class,
            "manifest": manifest,
            "pricing": pricing or {"tier": "free"},
        }

    return apps


def get_app_by_trigger(trigger: str) -> List[Dict]:
    """Get all apps that respond to a specific trigger.

    Args:
        trigger: Event type (pull_request, push, etc.)

    Returns:
        List of app info dicts
    """
    apps = load_apps()
    matching = []

    for name, info in apps.items():
        triggers = info["manifest"].get("triggers", [])
        if trigger in triggers:
            matching.append(info)

    return matching


def validate_manifest(manifest: Dict) -> List[str]:
    """Validate manifest structure. Returns list of errors."""
    errors = []

    required = ["name", "version", "triggers", "actions"]
    for field in required:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    if "triggers" in manifest:
        valid_triggers = ["pull_request", "push", "pull_request_comment", "issue"]
        for trigger in manifest["triggers"]:
            if trigger not in valid_triggers:
                errors.append(f"Invalid trigger: {trigger}")

    if "actions" in manifest:
        valid_actions = ["comment", "create_pr", "badge", "label", "approve", "status_check"]
        for action in manifest["actions"]:
            if action not in valid_actions:
                errors.append(f"Invalid action: {action}")

    return errors
