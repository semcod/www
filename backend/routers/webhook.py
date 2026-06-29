"""GitHub webhook handler for PR comments."""

import asyncio
import hmac
import hashlib
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
import httpx

from config import APP_URL, GITHUB_WEBHOOK_SECRET, LARGE_FILE_THRESHOLD
from services.github_client import get_installation_token
from services.scoring import score_to_grade
from store import audit_results

router = APIRouter()

# Keep references to background tasks to prevent garbage collection
_background_tasks = set()


@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if GITHUB_WEBHOOK_SECRET:
        expected = (
            "sha256="
            + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        )
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(401, "Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(body)

    if event == "pull_request":
        action = payload.get("action")
        if action in ("opened", "synchronize"):
            task = asyncio.create_task(_handle_pr_event(payload))
            # Store reference to prevent garbage collection
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)
            return {"status": "processing"}

    if event == "installation":
        action = payload.get("action")
        if action == "created":
            install_id = payload["installation"]["id"]
            sender = payload["sender"]["login"]
            print(f"[install] New installation {install_id} by {sender}")
            return {"status": "installed"}

    return {"status": "ignored"}


async def _handle_pr_event(payload: dict):
    """Analyze PR diff and post a comment with metrics."""
    pr = payload["pull_request"]
    repo_full = payload["repository"]["full_name"]
    pr_number = pr["number"]
    head_sha = pr["head"]["sha"]
    install_id = payload["installation"]["id"]

    token = await get_installation_token(install_id)
    if not token:
        print(f"[pr-bot] Failed to get token for installation {install_id}")
        return

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}/files",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        files = resp.json()

        analysis = _analyze_pr_files(files)
        report_url = f"{APP_URL}/report/{repo_full}"

        report = {
            "repo": repo_full,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "score": analysis["score"],
            "grade": analysis["grade"],
            "summary": _build_pr_summary(analysis),
            "large_files": analysis["large_files"],
            "risky_files": analysis["risky_files"],
            "has_tests": analysis["has_tests"],
            "file_types": analysis["file_types"],
            "report_url": report_url,
        }

        audit_results[f"github:{repo_full}#{pr_number}"] = {
            "status": "complete",
            **report,
        }

        comment = _build_pr_comment(analysis, repo_full, head_sha, report_url)

        await client.post(
            f"https://api.github.com/repos/{repo_full}/issues/{pr_number}/comments",
            json={"body": comment},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )

        grade = analysis["grade"]
        state = (
            "success"
            if grade in ("A+", "A", "B+")
            else "failure"
            if grade in ("D", "F")
            else "pending"
        )
        await client.post(
            f"https://api.github.com/repos/{repo_full}/statuses/{head_sha}",
            json={
                "state": state,
                "target_url": f"{APP_URL}/report/{repo_full}",
                "description": f"Code Health: {grade} ({analysis['score']}/100)",
                "context": "semcod/health",
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )

    print(f"[pr-bot] Commented on {repo_full}#{pr_number}: {grade} → {report_url}")


def _score_analysis(
    files_count: int,
    has_tests: bool,
    total_changes: int,
    large_files: list,
    risky_files: list,
) -> int:
    """Compute PR quality score from aggregated signals."""
    score = 85
    if not has_tests and total_changes > 50:
        score -= 15
    if files_count > 20:
        score -= 10
    elif files_count > 10:
        score -= 5
    score -= min(20, len(large_files) * 5)
    if risky_files and not has_tests:
        score -= 10
    return max(0, min(100, score))


def _analyze_pr_files(files: list[dict]) -> dict:
    """Analyze PR changed files for quality signals."""
    total_additions = 0
    total_deletions = 0
    large_files = []
    risky_files = []
    has_tests = False
    file_types: dict[str, int] = {}
    risky_patterns = ["migration", "schema", "config", "secret", ".env", "deploy"]

    for f in files:
        if not isinstance(f, dict):
            continue

        filename = f.get("filename", "")
        additions = f.get("additions", 0)
        deletions = f.get("deletions", 0)
        total_additions += additions
        total_deletions += deletions
        file_types[Path(filename).suffix] = file_types.get(Path(filename).suffix, 0) + 1

        if "test" in filename.lower() or "spec" in filename.lower():
            has_tests = True
        if additions + deletions > LARGE_FILE_THRESHOLD:
            large_files.append({"file": filename, "changes": additions + deletions})
        if any(p in filename.lower() for p in risky_patterns):
            risky_files.append(filename)

    score = _score_analysis(
        len(files),
        has_tests,
        total_additions + total_deletions,
        large_files,
        risky_files,
    )
    return {
        "score": score,
        "grade": score_to_grade(score),
        "files_changed": len(files),
        "additions": total_additions,
        "deletions": total_deletions,
        "large_files": large_files,
        "risky_files": risky_files,
        "has_tests": has_tests,
        "file_types": file_types,
    }


def _build_pr_summary(analysis: dict) -> list[str]:
    """Build short bullet summary for PR comments and reports."""
    summary = [
        f"{analysis['files_changed']} files changed",
        f"{analysis['additions']} additions / {analysis['deletions']} deletions",
    ]

    if analysis["large_files"]:
        summary.append(f"{len(analysis['large_files'])} large file(s) flagged")
    if analysis["risky_files"]:
        summary.append(f"{len(analysis['risky_files'])} risky file(s) need review")
    if (
        not analysis["has_tests"]
        and (analysis["additions"] + analysis["deletions"]) > 50
    ):
        summary.append("consider adding tests for this change set")

    return summary


def _build_pr_comment(analysis: dict, repo: str, sha: str, report_url: str) -> str:
    """Build markdown comment for PR."""
    grade = analysis["grade"]
    score = analysis["score"]

    emoji = {
        "A+": "🟢",
        "A": "🟢",
        "B+": "🟡",
        "B": "🟡",
        "C": "🟠",
        "D": "🔴",
        "F": "🔴",
    }
    grade_emoji = emoji.get(grade, "⚪")

    lines = [
        f"## {grade_emoji} Semcod Code Health: **{grade}** ({score}/100)",
        "",
        "> AI PR review summary",
        "",
        "",
        "| Metryka | Wartość |",
        "|---------|---------|",
        f"| Pliki zmienione | {analysis['files_changed']} |",
        f"| Dodane linie | +{analysis['additions']} |",
        f"| Usunięte linie | -{analysis['deletions']} |",
        f"| Testy w PR | {'✅ Tak' if analysis['has_tests'] else '⚠️ Brak'} |",
        f"| Raport | [open full report]({report_url}) |",
    ]

    if analysis["large_files"]:
        lines.append("")
        lines.append("### ⚠️ Duże pliki (>300 zmian)")
        for lf in analysis["large_files"][:5]:
            lines.append(f"- `{lf['file']}` — {lf['changes']} zmian")

    if analysis["risky_files"]:
        lines.append("")
        lines.append("### 🔍 Pliki wymagające review")
        for rf in analysis["risky_files"][:5]:
            lines.append(f"- `{rf}`")

    if not analysis["has_tests"] and analysis["additions"] > 50:
        lines.append("")
        lines.append(
            "> 💡 **Sugestia:** Ten PR dodaje znaczącą ilość kodu bez testów. "
            "Rozważ dodanie testów jednostkowych."
        )

    lines.extend(
        [
            "",
            "---",
            f"<sub>🔬 [Semcod]({APP_URL}) · audit: `{sha[:7]}` · "
            f"[full report]({report_url}) · "
            f"[Get this for your repo (free)]({APP_URL})</sub>",
        ]
    )

    return "\n".join(lines)
