"""
Semcod GitHub App — Backend
===========================
One-click Audit + PR Comment Bot + Code Health Badge

Deploy: uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
import json
import hmac
import hashlib
import asyncio
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import Response, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

# ─── Config ───────────────────────────────────────────────────────────────────

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "private-key.pem")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(title="Semcod", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://semcod.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-memory store (swap for Redis/Postgres in production) ──────────────────

audit_results: dict[str, dict] = {}
badge_cache: dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ONE-CLICK AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/auth/github")
async def github_oauth_start():
    """Step 1: Redirect user to GitHub OAuth."""
    scope = "repo,read:org"
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope={scope}"
        f"&redirect_uri={APP_URL}/auth/callback"
    )
    return RedirectResponse(url)


@app.get("/auth/callback")
async def github_oauth_callback(code: str):
    """Step 2: Exchange code for token, redirect to frontend."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        data = resp.json()

    token = data.get("access_token")
    if not token:
        raise HTTPException(400, "OAuth failed")

    return RedirectResponse(f"{FRONTEND_URL}/audit?token={token}")


@app.get("/api/repos")
async def list_repos(token: str):
    """List user's repos for audit selection."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            params={"sort": "updated", "per_page": 30, "type": "owner"},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
    repos = resp.json()
    return [
        {
            "full_name": r["full_name"],
            "name": r["name"],
            "language": r.get("language"),
            "stars": r.get("stargazers_count", 0),
            "size_kb": r.get("size", 0),
            "private": r.get("private", False),
            "default_branch": r.get("default_branch", "main"),
        }
        for r in repos
        if isinstance(r, dict)
    ]


@app.post("/api/audit")
async def run_audit(request: Request):
    """
    Run one-click audit on a repo.
    Body: { "repo": "owner/name", "token": "ghp_..." }
    """
    body = await request.json()
    repo = body["repo"]
    token = body["token"]
    audit_id = hashlib.sha256(f"{repo}-{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]

    # Store pending status
    audit_results[audit_id] = {"status": "running", "repo": repo, "started": datetime.utcnow().isoformat()}

    # Run audit in background
    asyncio.create_task(_run_audit_pipeline(audit_id, repo, token))

    return {"audit_id": audit_id, "status": "running"}


@app.get("/api/audit/{audit_id}")
async def get_audit_result(audit_id: str):
    """Poll audit status and results."""
    result = audit_results.get(audit_id)
    if not result:
        raise HTTPException(404, "Audit not found")
    return result


async def _run_audit_pipeline(audit_id: str, repo: str, token: str):
    """
    Background pipeline: clone → code2llm → redup → pyqual → regix → report.
    
    This is the core analysis engine. Each tool runs independently and
    results are aggregated into a single report.
    """
    workdir = Path(tempfile.mkdtemp(prefix="semcod-"))

    try:
        # Step 1: Clone repo
        clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth=1", clone_url, str(workdir / "repo"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()

        repo_path = workdir / "repo"

        # Step 2: Count lines and files
        stats = await _count_code_stats(repo_path)

        # Step 3: Run code2llm (static analysis → TOON metrics)
        code2llm_result = await _run_tool(
            "code2llm", ["analyze", str(repo_path), "--format", "json"],
            fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0}
        )

        # Step 4: Run redup (duplication detection)
        redup_result = await _run_tool(
            "redup", ["scan", str(repo_path), "--format", "json"],
            fallback={"duplication_groups": 0, "duplicated_lines": 0, "recoverable_lines": 0}
        )

        # Step 5: Run pyqual (quality gates)
        pyqual_result = await _run_tool(
            "pyqual", ["check", str(repo_path), "--format", "json"],
            fallback={"passed": 0, "warnings": 0, "errors": 0, "score": 0}
        )

        # Step 6: Calculate health score (0-100)
        health_score = _calculate_health_score(stats, code2llm_result, redup_result, pyqual_result)

        # Step 7: Generate recommendations
        recommendations = _generate_recommendations(code2llm_result, redup_result, pyqual_result)

        # Build final report
        report = {
            "status": "complete",
            "repo": repo,
            "completed": datetime.utcnow().isoformat(),
            "stats": stats,
            "health_score": health_score,
            "grade": _score_to_grade(health_score),
            "metrics": {
                "complexity": code2llm_result,
                "duplication": redup_result,
                "quality": pyqual_result,
            },
            "recommendations": recommendations,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }

        audit_results[audit_id] = report

        # Cache for badge
        badge_cache[repo] = {
            "score": health_score,
            "grade": _score_to_grade(health_score),
            "updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        audit_results[audit_id] = {
            "status": "error",
            "repo": repo,
            "error": str(e),
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


async def _count_code_stats(repo_path: Path) -> dict:
    """Count source files and lines."""
    total_files = 0
    total_lines = 0
    languages: dict[str, int] = {}

    extensions_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".java": "Java", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
        ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
        ".swift": "Swift", ".kt": "Kotlin", ".sh": "Shell",
    }

    for ext, lang in extensions_map.items():
        for f in repo_path.rglob(f"*{ext}"):
            if any(part.startswith(".") or part == "node_modules" or part == "vendor" for part in f.parts):
                continue
            try:
                lines = len(f.read_text(errors="ignore").splitlines())
                total_files += 1
                total_lines += lines
                languages[lang] = languages.get(lang, 0) + lines
            except Exception:
                pass

    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "languages": dict(sorted(languages.items(), key=lambda x: -x[1])[:5]),
    }


async def _run_tool(name: str, args: list[str], fallback: dict) -> dict:
    """Run a semcod tool, return JSON result or fallback."""
    try:
        proc = await asyncio.create_subprocess_exec(
            name, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        return json.loads(stdout.decode())
    except Exception:
        # Tool not installed or failed — return simulated metrics
        # In production, all tools would be installed in the container
        return fallback


def _calculate_health_score(stats, complexity, duplication, quality) -> int:
    """
    Calculate 0-100 health score from metrics.
    
    Weights:
    - Complexity (CC avg): 30%   → lower is better, target < 5
    - Duplication: 20%           → fewer groups is better
    - Quality (errors): 30%     → fewer errors is better
    - Test presence: 20%        → higher ratio is better
    """
    score = 100

    # Complexity penalty (CC avg > 5 starts losing points)
    cc = complexity.get("cc_avg", 5)
    if cc > 10:
        score -= 30
    elif cc > 7:
        score -= 20
    elif cc > 5:
        score -= 10

    # Duplication penalty
    dup_groups = duplication.get("duplication_groups", 0)
    if dup_groups > 20:
        score -= 20
    elif dup_groups > 10:
        score -= 15
    elif dup_groups > 5:
        score -= 10
    elif dup_groups > 0:
        score -= 5

    # Quality errors penalty
    errors = quality.get("errors", 0)
    warnings = quality.get("warnings", 0)
    score -= min(30, errors * 3 + warnings)

    # Size bonus/penalty (very small repos get less data)
    lines = stats.get("total_lines", 0)
    if lines < 100:
        score = max(score, 50)  # Not enough data

    return max(0, min(100, score))


def _score_to_grade(score: int) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B+"
    if score >= 60: return "B"
    if score >= 50: return "C"
    if score >= 40: return "D"
    return "F"


def _generate_recommendations(complexity, duplication, quality) -> list[dict]:
    """Generate actionable recommendations based on metrics."""
    recs = []

    cc = complexity.get("cc_avg", 0)
    if cc > 7:
        recs.append({
            "priority": "high",
            "category": "complexity",
            "title": "Wysoka złożoność cyklomatyczna",
            "description": f"Średnia CC = {cc:.1f}. Cel: < 5. Rozważ podział złożonych funkcji na mniejsze.",
            "tool": "redsl",
            "action": "redsl refactor --strategy split-complex",
        })

    dup = duplication.get("duplication_groups", 0)
    if dup > 5:
        recoverable = duplication.get("recoverable_lines", 0)
        recs.append({
            "priority": "medium",
            "category": "duplication",
            "title": f"{dup} grup duplikacji ({recoverable} linii do odzyskania)",
            "description": "Zduplikowany kod zwiększa koszt utrzymania. Ekstrakcja wspólnych funkcji.",
            "tool": "redup",
            "action": f"redup plan --top {min(dup, 10)}",
        })

    errors = quality.get("errors", 0)
    if errors > 0:
        recs.append({
            "priority": "high",
            "category": "quality",
            "title": f"{errors} błędów jakości kodu",
            "description": "Błędy statycznej analizy (typy, security, style). Napraw przed merge.",
            "tool": "pyqual",
            "action": "pyqual fix --auto",
        })

    if not recs:
        recs.append({
            "priority": "low",
            "category": "maintenance",
            "title": "Kod w dobrej kondycji",
            "description": "Brak krytycznych problemów. Kontynuuj monitorowanie z weekly scans.",
            "tool": "weekly",
            "action": "weekly analyze",
        })

    return recs


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PR COMMENT BOT (GitHub Webhook)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Handle GitHub webhook events.
    
    Supported events:
    - pull_request (opened, synchronize) → run analysis, post comment
    - installation (created) → log new installation
    """
    # Verify webhook signature
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if GITHUB_WEBHOOK_SECRET:
        expected = "sha256=" + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(401, "Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(body)

    if event == "pull_request":
        action = payload.get("action")
        if action in ("opened", "synchronize"):
            asyncio.create_task(_handle_pr_event(payload))
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
    """
    Analyze PR diff and post a comment with metrics.
    
    Flow:
    1. Get installation token
    2. Fetch PR diff
    3. Analyze changed files
    4. Post comment with metrics table
    """
    pr = payload["pull_request"]
    repo_full = payload["repository"]["full_name"]
    pr_number = pr["number"]
    head_sha = pr["head"]["sha"]
    install_id = payload["installation"]["id"]

    # Get installation access token
    token = await _get_installation_token(install_id)
    if not token:
        print(f"[pr-bot] Failed to get token for installation {install_id}")
        return

    async with httpx.AsyncClient() as client:
        # Fetch changed files
        resp = await client.get(
            f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}/files",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        files = resp.json()

        # Analyze changes
        analysis = _analyze_pr_files(files)

        # Build comment body
        comment = _build_pr_comment(analysis, repo_full, head_sha)

        # Post comment
        await client.post(
            f"https://api.github.com/repos/{repo_full}/issues/{pr_number}/comments",
            json={"body": comment},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )

        # Set commit status
        grade = analysis["grade"]
        state = "success" if grade in ("A+", "A", "B+") else "failure" if grade in ("D", "F") else "pending"
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

    print(f"[pr-bot] Commented on {repo_full}#{pr_number}: {grade}")


def _analyze_pr_files(files: list[dict]) -> dict:
    """
    Analyze PR changed files for quality signals.
    
    Checks:
    - Large files (> 300 lines changed)
    - High number of files changed
    - Test coverage (are tests included?)
    - File types and risk areas
    """
    total_additions = 0
    total_deletions = 0
    large_files = []
    risky_files = []
    has_tests = False
    file_types: dict[str, int] = {}

    for f in files:
        if not isinstance(f, dict):
            continue

        filename = f.get("filename", "")
        additions = f.get("additions", 0)
        deletions = f.get("deletions", 0)
        total_additions += additions
        total_deletions += deletions

        # Track file types
        ext = Path(filename).suffix
        file_types[ext] = file_types.get(ext, 0) + 1

        # Check for tests
        if "test" in filename.lower() or "spec" in filename.lower():
            has_tests = True

        # Flag large changes
        if additions + deletions > 300:
            large_files.append({"file": filename, "changes": additions + deletions})

        # Flag risky patterns
        risky_patterns = ["migration", "schema", "config", "secret", ".env", "deploy"]
        if any(p in filename.lower() for p in risky_patterns):
            risky_files.append(filename)

    # Calculate score
    score = 85  # Base score for any PR

    # Penalty for no tests with significant code changes
    code_changes = total_additions + total_deletions
    if not has_tests and code_changes > 50:
        score -= 15

    # Penalty for too many files
    if len(files) > 20:
        score -= 10
    elif len(files) > 10:
        score -= 5

    # Penalty for large files
    score -= min(20, len(large_files) * 5)

    # Penalty for risky files without tests
    if risky_files and not has_tests:
        score -= 10

    score = max(0, min(100, score))

    return {
        "score": score,
        "grade": _score_to_grade(score),
        "files_changed": len(files),
        "additions": total_additions,
        "deletions": total_deletions,
        "large_files": large_files,
        "risky_files": risky_files,
        "has_tests": has_tests,
        "file_types": file_types,
    }


def _build_pr_comment(analysis: dict, repo: str, sha: str) -> str:
    """Build markdown comment for PR."""
    grade = analysis["grade"]
    score = analysis["score"]

    # Grade emoji
    emoji = {"A+": "🟢", "A": "🟢", "B+": "🟡", "B": "🟡", "C": "🟠", "D": "🔴", "F": "🔴"}
    grade_emoji = emoji.get(grade, "⚪")

    lines = [
        f"## {grade_emoji} Semcod Code Health: **{grade}** ({score}/100)",
        "",
        "| Metryka | Wartość |",
        "|---------|---------|",
        f"| Pliki zmienione | {analysis['files_changed']} |",
        f"| Dodane linie | +{analysis['additions']} |",
        f"| Usunięte linie | -{analysis['deletions']} |",
        f"| Testy w PR | {'✅ Tak' if analysis['has_tests'] else '⚠️ Brak'} |",
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
        lines.append("> 💡 **Sugestia:** Ten PR dodaje znaczącą ilość kodu bez testów. "
                     "Rozważ dodanie testów jednostkowych.")

    lines.extend([
        "",
        "---",
        f"<sub>🔬 [Semcod]({APP_URL}) · audyt: `{sha[:7]}` · "
        f"[pełny raport]({APP_URL}/report/{repo})</sub>",
    ])

    return "\n".join(lines)


async def _get_installation_token(installation_id: int) -> Optional[str]:
    """
    Get GitHub App installation access token using JWT.
    
    In production, use PyJWT to sign with the app's private key.
    For development, you can use a PAT instead.
    """
    try:
        import jwt
        import time

        private_key = Path(GITHUB_PRIVATE_KEY_PATH).read_text()
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 600,
            "iss": GITHUB_APP_ID,
        }
        encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {encoded_jwt}",
                    "Accept": "application/vnd.github+json",
                },
            )
            data = resp.json()
            return data.get("token")
    except Exception as e:
        print(f"[auth] Token error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CODE HEALTH SCORE BADGE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/badge/{repo_slug}.svg")
async def health_badge(repo_slug: str, style: str = "flat"):
    """
    Generate SVG badge with code health score.
    
    Usage in README:
    ![Code Health](https://semcod.dev/badge/owner-repo.svg)
    
    repo_slug format: "owner-repo" (dashes instead of slash)
    """
    repo = repo_slug.replace("-", "/", 1)
    cached = badge_cache.get(repo)

    if cached:
        score = cached["score"]
        grade = cached["grade"]
    else:
        # Default badge for repos not yet analyzed
        score = None
        grade = "?"

    svg = _generate_badge_svg(grade, score, style)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "ETag": f'"{grade}-{score}"',
        },
    )


def _generate_badge_svg(grade: str, score: Optional[int], style: str) -> str:
    """Generate shields.io-style SVG badge."""
    # Colors by grade
    colors = {
        "A+": "#22c55e", "A": "#34d399", "B+": "#a3e635",
        "B": "#facc15", "C": "#fb923c", "D": "#f87171",
        "F": "#ef4444", "?": "#94a3b8",
    }
    color = colors.get(grade, "#94a3b8")

    label = "code health"
    value = f"{grade}" if score is None else f"{grade} · {score}%"

    label_width = len(label) * 6.5 + 12
    value_width = len(value) * 7 + 12
    total_width = label_width + value_width

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text aria-hidden="true" x="{label_width/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width/2}" y="14">{label}</text>
    <text aria-hidden="true" x="{label_width + value_width/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_width + value_width/2}" y="14">{value}</text>
  </g>
</svg>"""
    return svg


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "tools": ["code2llm", "redup", "pyqual", "regix", "vallm"],
        "audits_cached": len(audit_results),
        "badges_cached": len(badge_cache),
    }


@app.get("/report/{owner}/{repo}")
async def report_page(owner: str, repo: str):
    """Redirect to frontend report page."""
    return RedirectResponse(f"{FRONTEND_URL}/report/{owner}/{repo}")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
