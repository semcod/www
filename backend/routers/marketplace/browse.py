"""Marketplace browse endpoints - preview and list apps."""
from typing import Dict, List
from fastapi import APIRouter, Depends

from adapters import get_adapter_for_event
from apps.base import AppContext
from events.models import Event, EventType, ProviderType
from routers.auth import get_current_user
from routers.marketplace.models import PreviewRequest, PreviewResponse

router = APIRouter(tags=["marketplace"])


@router.post("/preview", response_model=PreviewResponse)
async def preview_pr_comment(
    request: PreviewRequest,
    user: dict = Depends(get_current_user),
) -> PreviewResponse:
    """Generate preview of PR comment for a repository.

    This endpoint simulates analysis on a sample diff to show
    users what the bot would comment before they install.
    """
    from apps.registry import get_registry

    # Sample diff for preview (in production, fetch from repo's last PR)
    sample_diff = """
    - function calculateTotal(items) {
    -   let total = 0;
    -   for (let i = 0; i < items.length; i++) {
    -     total += items[i].price;
    -   }
    -   return total;
    - }
    + function calculateTotal(items) {
    +   return items.reduce((sum, item) => sum + item.price, 0);
    + }
    """

    # Run preview analysis through apps registry
    registry = get_registry()

    # Create mock event
    event = Event(
        type=EventType.PULL_REQUEST,
        provider=ProviderType(request.provider),
        repo=request.repo,
        action="opened",
        raw_payload={},
    )

    # Build context
    context = AppContext(
        repo=request.repo,
        event_type="pull_request",
        provider=request.provider,
        diff=sample_diff,
    )

    # Run apps and collect results
    results = registry.process_event(event)

    # Aggregate scores
    scores = []
    all_issues = []

    for app_name, result in results.items():
        if result.score is not None:
            scores.append(result.score)
        all_issues.extend(result.issues)

    avg_score = int(sum(scores) / len(scores)) if scores else 75

    # Format comment
    comment = _format_preview_comment(request.repo, avg_score, all_issues)

    return PreviewResponse(
        score=avg_score,
        comment=comment,
        issues=all_issues[:5],  # Limit to 5 issues
        suggested_patch=None,  # Could add auto-fix generation here
    )


@router.get("/apps")
async def list_apps() -> List[Dict]:
    """List all available marketplace apps."""
    from apps.registry import get_registry
    registry = get_registry()
    return registry.list_apps()


def _format_preview_comment(repo: str, score: int, issues: List[Dict]) -> str:
    """Format preview comment like GitHub PR comment."""
    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"

    comment = f"""## {emoji} Semcod Preview Analysis

**Repository:** `{repo}`
**Health Score:** {score}/100 (Grade {grade})

"""

    if issues:
        comment += "### Issues Found\n"
        for issue in issues[:5]:
            icon = "🔴" if issue.get("severity") == "high" else "🟡"
            comment += f"- {icon} **{issue.get('type', 'issue')}**: {issue.get('message', '')}\n"
        comment += "\n"
    else:
        comment += "✅ No major issues detected!\n\n"

    comment += """### Next Steps
- Install Semcod to enable automatic PR analysis
- Enable auto-fix to generate patches automatically

---
*Powered by [Semcod](https://semcod.com)*
"""

    return comment
