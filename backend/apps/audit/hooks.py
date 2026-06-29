"""Audit App - Event hooks for PR comments."""

from apps.base import AppContext, AppResult


def on_pr_comment(event, context: AppContext) -> AppResult:
    """Handle PR comment commands.

    Commands:
    - @semcod audit - Run full audit
    - @semcod explain [issue] - Explain specific issue
    - @semcod ignore [issue] - Ignore issue (for maintainers)
    """
    comment = event.get("comment", {}).get("body", "")

    if "@semcod audit" in comment:
        # Trigger full audit
        from .pipeline import AuditApp

        app = AuditApp()
        return app.run_pipeline(context)

    if "@semcod explain" in comment:
        # Explain specific issue
        return AppResult(
            status="success",
            details={"message": "Issue explanation requested"},
        )

    return AppResult(status="skipped")
