"""Scan service — facade over db_module for all scan/audit/badge operations.

Routers should import from here instead of directly from database/db_module.
"""

from database import (
    save_scan,
    get_recent_scans,
    get_total_scan_count,
    get_repo_scans,
    save_audit_result,
    get_audit_result,
    save_badge_cache,
    get_badge_cache,
)

__all__ = [
    "save_scan",
    "get_recent_scans",
    "get_total_scan_count",
    "get_repo_scans",
    "save_audit_result",
    "get_audit_result",
    "save_badge_cache",
    "get_badge_cache",
]
