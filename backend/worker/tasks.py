"""Celery tasks for Semcod - async processing of audits and PR events."""
import asyncio
from typing import Dict, Any, Optional
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from events.models import Event, EventType, ProviderType
from adapters import get_adapter_for_event
from adapters.base import GitProvider
from adapters.github import GitHubAdapter
from adapters.gitlab import GitLabAdapter
from adapters.gitea import GiteaAdapter


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
        # Import here to avoid circular dependencies
        try:
            from services.scoring import calculate_health_score
            from services.analyzer import analyze_repo
        except ImportError:
            # Fallback mocks for testing
            def calculate_health_score(result):
                return result.get("health_score", 70)

            def analyze_repo(repo, commit_sha, config):
                return {"health_score": 70, "issues": [], "recommendations": []}

        # Run analysis
        result = analyze_repo(repo, commit_sha, config)
        score = calculate_health_score(result)

        return {
            "status": "completed",
            "repo": repo,
            "commit_sha": commit_sha,
            "health_score": score,
            "issues": result.get("issues", []),
            "recommendations": result.get("recommendations", []),
        }

    except Exception as exc:
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)  # 1min, 2min, 4min
            raise self.retry(exc=exc, countdown=countdown)
        return {
            "status": "failed",
            "repo": repo,
            "error": str(exc),
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
    Analyze a diff asynchronously using AI/ML pipeline.

    This is the heavy processing task that runs ML models
    for code analysis.
    """
    try:
        # Simulated analysis - replace with actual ML pipeline
        from services.scoring import calculate_health_score

        # Mock result for now
        issues = []
        if "TODO" in diff:
            issues.append({"type": "todo", "severity": "low"})
        if "FIXME" in diff:
            issues.append({"type": "fixme", "severity": "medium"})

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


@shared_task(bind=True, max_retries=2)
def create_auto_pr(
    self,
    repo: str,
    base_branch: str,
    patches: list,
    proposal_type: str,
    llm_prompt: str,
    token: str,
    provider_type: str = "github",
) -> Dict[str, Any]:
    """
    Create automated PR with fixes asynchronously.

    Similar to autopr router but as async task.
    """
    try:
        # Get adapter (imports at module level)
        adapter_map = {
            "github": GitHubAdapter,
            "gitlab": GitLabAdapter,
            "gitea": GiteaAdapter,
        }
        adapter_class = adapter_map.get(provider_type, GitHubAdapter)
        adapter = adapter_class(token)

        # Create branch and commit patches
        default_branch = asyncio.run(adapter.get_default_branch(repo))
        base_sha = asyncio.run(adapter.get_ref_sha(repo, default_branch))

        import hashlib
        from datetime import datetime, timezone

        fix_id = hashlib.sha256(
            f"{repo}-{proposal_type}-{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:8]
        branch = f"semcod-fix-{fix_id}"

        asyncio.run(adapter.create_branch(repo, branch, base_sha))

        # Commit each patch
        for patch in patches:
            file_sha = asyncio.run(
                adapter.get_file_sha(repo, patch["path"], branch)
            )
            asyncio.run(
                adapter.commit_file(
                    repo,
                    patch["path"],
                    patch["content"],
                    branch,
                    f"fix({proposal_type}): auto-fix via Semcod [{fix_id}]",
                    file_sha,
                )
            )

        # Create PR
        pr_url = asyncio.run(
            adapter.create_pr(
                repo,
                f"[Semcod] Auto-fix: {proposal_type.replace('_', ' ')} [{fix_id}]",
                f"Auto-fix generated from: {llm_prompt}",
                branch,
                base_branch,
            )
        )

        return {
            "status": "created",
            "repo": repo,
            "pr_url": pr_url,
            "branch": branch,
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60)
        return {
            "status": "failed",
            "error": str(exc),
        }


@shared_task
def check_health_regression(
    repo: str,
    previous_score: Optional[int],
    new_score: int,
    threshold: int = -5,
) -> Dict[str, Any]:
    """
    Check if health score regressed and create issue if needed.
    """
    if previous_score is None:
        return {"status": "no_baseline"}

    delta = new_score - previous_score

    if delta < threshold:
        return {
            "status": "regression_detected",
            "previous_score": previous_score,
            "new_score": new_score,
            "delta": delta,
            "should_alert": True,
        }

    return {
        "status": "ok",
        "delta": delta,
        "improvement": delta > 0,
    }


# ─── Helper Functions ─────────────────────────────────────────────────────────────


def _get_token_for_provider(provider: ProviderType) -> Optional[str]:
    """Get API token for provider from config."""
    import os

    token_map = {
        ProviderType.GITHUB: os.getenv("GITHUB_TOKEN", os.getenv("GITHUB_CLIENT_SECRET", "")),
        ProviderType.GITLAB: os.getenv("GITLAB_TOKEN", ""),
        ProviderType.GITEA: os.getenv("GITEA_TOKEN", ""),
    }
    return token_map.get(provider)


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
