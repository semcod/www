"""Scan-related Celery tasks - audits and diff analysis."""
import asyncio
from typing import Dict, Any

try:
    from celery import shared_task
    from celery.exceptions import MaxRetriesExceededError
    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task, MaxRetriesExceededError  # type: ignore[assignment]

from events.models import Event, EventType, ProviderType
from adapters import get_adapter_for_event


@shared_task(bind=True, max_retries=3)
def run_audit(self, repo: str, commit_sha: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run code audit on a repository asynchronously.

    Args:
        repo: Full repo name (owner/repo)
        commit_sha: Commit SHA to analyze
        config: Audit configuration (language, thresholds, etc.)

    Returns:
        Audit result with health score, issues, recommendations
    """
    try:
        # Import analysis functions
        from services.scoring import calculate_health_score
        from services.analyzer import analyze_repo
    except ImportError as e:
        return {
            "status": "failed",
            "repo": repo,
            "error": f"Analysis modules not available: {e}",
        }

    # Run analysis
    result = analyze_repo(repo, commit_sha, config)
    score = result.get("health_score", 70)  # Use score from analyze_repo

    # Record usage if tenant_id provided
    tenant_id = config.get("tenant_id")
    if tenant_id:
        try:
            from services.billing import get_usage_tracker, BillingEventType
            usage = get_usage_tracker().record_usage(
                tenant_id=tenant_id,
                event_type=BillingEventType.PR_ANALYSIS,
                quantity=1,
                metadata={"repo": repo, "commit_sha": commit_sha},
            )
            result["billing"] = {
                "usage_recorded": True,
                "cost_cents": usage["cost_cents"],
                "within_limit": usage["within_limit"],
            }
        except Exception as e:
            print(f"[run_audit] Failed to record usage: {e}")

    return {
        "status": "completed",
        "repo": repo,
        "commit_sha": commit_sha,
        "health_score": score,
        "issues": result.get("issues", []),
        "recommendations": result.get("recommendations", []),
    }


@shared_task(bind=True, max_retries=3)
def process_pr_event(self, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process pull request event asynchronously.

    Flow:
    1. Parse event from dict
    2. Get diff content
    3. Run analysis
    4. Comment results
    """
    try:
        from events.models import Event, EventType, ProviderType

        # Reconstruct event
        event = Event(
            type=EventType(event_dict["type"]),
            provider=ProviderType(event_dict["provider"]),
            repo=event_dict["repo"],
            pr_id=event_dict.get("pr_id"),
            branch=event_dict.get("branch"),
            base_branch=event_dict.get("base_branch"),
            commit_sha=event_dict.get("commit_sha"),
            author=event_dict.get("author"),
            action=event_dict.get("action"),
            raw_payload=event_dict.get("raw_payload", {}),
        )

        # Skip if not actionable
        if event.action not in ("opened", "synchronize", "reopened"):
            return {"status": "skipped", "reason": "non-actionable action"}

        # Get token and adapter
        token = _get_token_for_provider(event.provider)
        if not token:
            return {"status": "skipped", "reason": "no token configured"}

        provider = get_adapter_for_event(event, token)

        # Get diff and analyze
        diff = asyncio.run(provider.get_pr_diff(event.repo, event.pr_id))
        analysis = asyncio.run(_analyze_diff(diff, event.repo))

        # Post comment with results
        comment = _format_pr_comment(event, analysis)
        comment_url = asyncio.run(
            provider.comment_on_pr(event.repo, event.pr_id, comment)
        )

        return {
            "status": "completed",
            "repo": event.repo,
            "pr_id": event.pr_id,
            "health_score": analysis.get("health_score"),
            "issues_found": len(analysis.get("issues", [])),
            "comment_url": comment_url,
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        return {
            "status": "failed",
            "error": str(exc),
        }


@shared_task
def process_push_event(event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process push event - trigger analysis for default branch.
    """
    from events.models import Event, EventType, ProviderType

    event = Event(
        type=EventType(event_dict["type"]),
        provider=ProviderType(event_dict["provider"]),
        repo=event_dict["repo"],
        branch=event_dict.get("branch"),
        commits=event_dict.get("commits", []),
        raw_payload=event_dict.get("raw_payload", {}),
    )

    # Only process default branches
    if event.branch not in ("main", "master"):
        return {"status": "skipped", "reason": "not default branch"}

    # Schedule audit for each commit (or just latest)
    if event.commits:
        latest = event.commits[-1]
        task = run_audit.delay(
            repo=event.repo,
            commit_sha=latest.get("id"),
            config={"branch": event.branch},
        )
        return {
            "status": "scheduled",
            "repo": event.repo,
            "branch": event.branch,
            "audit_task_id": task.id,
        }

    return {"status": "skipped", "reason": "no commits"}


@shared_task(bind=True, max_retries=2)
def analyze_diff(self, repo: str, diff: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a diff asynchronously using actual analysis.

    This analyzes diff content for code quality issues.
    """
    try:
        from services.scoring import calculate_health_score
        import re

        # Parse diff for actual issues
        issues = []
        
        # Check for TODO/FIXME comments
        if "TODO" in diff:
            issues.append({"type": "todo", "severity": "low"})
        if "FIXME" in diff:
            issues.append({"type": "fixme", "severity": "medium"})
        
        # Check for complexity indicators
        if diff.count("if ") > 10:
            issues.append({"type": "high_complexity", "severity": "medium"})
        
        # Check for long lines (>100 chars in diff)
        for line in diff.split("\n"):
            if line.startswith("+") and len(line) > 100:
                issues.append({"type": "long_line", "severity": "low"})
                break

        score = max(0, 100 - len(issues) * 10)

        return {
            "status": "completed",
            "repo": repo,
            "health_score": score,
            "issues": issues,
            "lines_changed": diff.count("\n"),
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30)
        raise


# Helper functions
def _get_token_for_provider(provider: ProviderType) -> str:
    """Get API token for provider from config."""
    import os

    token_map = {
        ProviderType.GITHUB: os.getenv("GITHUB_TOKEN", os.getenv("GITHUB_CLIENT_SECRET", "")),
        ProviderType.GITLAB: os.getenv("GITLAB_TOKEN", ""),
        ProviderType.GITEA: os.getenv("GITEA_TOKEN", ""),
    }
    return token_map.get(provider, "")


async def _analyze_diff(diff: str, repo: str) -> Dict[str, Any]:
    """Run analysis on diff content."""
    # Placeholder - integrate with actual analysis service
    from services.scoring import calculate_health_score

    # Simulated analysis
    issues = []
    if "complex" in diff.lower():
        issues.append({"type": "complexity", "severity": "medium"})
    if "duplicate" in diff.lower():
        issues.append({"type": "duplication", "severity": "high"})

    score = max(0, 100 - len(issues) * 15)

    return {
        "health_score": score,
        "issues": issues,
        "grade": "B" if score > 80 else "C",
    }


def _format_pr_comment(event: Event, analysis: Dict[str, Any]) -> str:
    """Format PR comment with analysis results."""
    score = analysis.get("health_score", 0)
    grade = analysis.get("grade", "C")
    issues = analysis.get("issues", [])

    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

    comment = f"""## {emoji} Semcod Analysis Report

**Repository:** `{event.repo}`
**Branch:** `{event.branch}` → `{event.base_branch}`
**Health Score:** {score}/100 (Grade {grade})

"""

    if issues:
        comment += "### Issues Found\n"
        for issue in issues:
            icon = "🔴" if issue["severity"] == "high" else "🟡"
            comment += f"- {icon} **{issue['type']}** ({issue['severity']})\n"
        comment += "\n"

    comment += """---
*Powered by [Semcod](https://semcod.com) - AI Code Health Analysis*
"""

    return comment
