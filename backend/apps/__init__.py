"""Apps module - marketplace plugins for Semcod.

Each app is a self-contained plugin with:
- manifest.yaml - metadata, triggers, permissions
- pipeline.py - main analysis logic
- hooks.py - event handlers
- pricing.json - billing configuration
"""

from .registry import AppRegistry, get_registry
from .loader import load_apps, load_app
from .base import AppBase

__all__ = ["AppRegistry", "get_registry", "load_apps", "load_app", "AppBase"]
