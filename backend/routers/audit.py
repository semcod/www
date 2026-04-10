"""Audit endpoints and analysis pipeline."""

import asyncio
import hashlib
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from config import APP_URL, SCAN_HISTORY_LIMIT
from services.analyzer import count_code_stats, run_tool
from services.scoring import calculate_health_score, generate_recommendations, score_to_grade
from database import save_scan, get_recent_scans, save_audit_result, get_audit_result, save_badge_cache, get_badge_cache
from routers.auth import get_current_user

router = APIRouter()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _schedule_background_task(coroutine):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        coroutine.close()
        return
    loop.create_task(coroutine)


@router.post("/api/audit")
async def run_audit(request: Request, user: dict = Depends(get_current_user)):
    """Run one-click audit on a repo. Requires authentication."""
    body = await request.json()
    repo = body["repo"]
    token = user["github_token"]
    audit_id = hashlib.sha256(
        f"{repo}-{_utc_now_iso()}".encode()
    ).hexdigest()[:12]

    # Save initial audit status to database
    save_audit_result(audit_id, {
        "status": "running",
        "repo": repo,
        "started": _utc_now_iso(),
    })

    _schedule_background_task(_run_audit_pipeline(audit_id, repo, token))
    return {"audit_id": audit_id, "status": "running"}


@router.get("/api/audit/{audit_id}")
async def get_audit_result_endpoint(audit_id: str):
    """Poll audit status and results."""
    result = get_audit_result(audit_id)
    if not result:
        raise HTTPException(404, "Audit not found")
    return result


@router.get("/api/scans/recent")
async def get_recent_scans_api(limit: int = 100):
    """Get list of recent scans with metrics."""
    # Try to get from SQLite first, fall back to in-memory
    try:
        scans = get_recent_scans(limit)
        total = len(scans)
    except Exception:
        scans = scan_history[:limit]
        total = len(scan_history)
    
    return {
        "scans": scans,
        "total": total,
    }


@router.post("/api/analyze")
async def analyze_repo(request: Request):
    """Analyze any public repository by URL (sandbox mode)."""
    body = await request.json()
    repo_url = body.get("repo_url", "")
    sandbox = body.get("sandbox", False)

    if not repo_url:
        raise HTTPException(400, "repo_url required")

    # Parse owner/repo from URL
    match = (
        re.search(r"github\.com/([^/]+)/([^/\.]+)", repo_url)
        or re.search(r"gitlab\.com/([^/]+)/([^/\.]+)", repo_url)
        or re.search(r"bitbucket\.org/([^/]+)/([^/\.]+)", repo_url)
    )

    if not match:
        ssh_match = re.search(r":([^/]+)/([^/\.]+)\.?", repo_url)
        if ssh_match:
            match = ssh_match

    if not match:
        raise HTTPException(400, "Could not parse owner/repo from URL")

    owner, repo = match.group(1), match.group(2)
    audit_id = hashlib.sha256(
        f"{owner}/{repo}-{_utc_now_iso()}".encode()
    ).hexdigest()[:12]

    # Save initial audit status to database
    save_audit_result(audit_id, {
        "status": "running",
        "repo": f"{owner}/{repo}",
        "sandbox": sandbox,
        "started": _utc_now_iso(),
    })

    _schedule_background_task(_run_sandbox_analysis(audit_id, repo_url, f"{owner}/{repo}"))
    return {"audit_id": audit_id, "status": "running", "sandbox": True}


async def _run_audit_pipeline(audit_id: str, repo: str, token: str):
    """Background pipeline: clone → code2llm → redup → pyqual → report."""
    workdir = Path(tempfile.mkdtemp(prefix="semcod-"))

    try:
        clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth=1",
            clone_url,
            str(workdir / "repo"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()

        repo_path = workdir / "repo"
        stats = await count_code_stats(repo_path)

        code2llm_result = await run_tool(
            "code2llm",
            ["analyze", str(repo_path), "--format", "json"],
            fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0},
        )

        # Generate file contents for LLM prompts
        code2llm_files = await run_tool(
            "code2llm",
            [str(repo_path), "-f", "all", "--format", "json"],
            fallback={"files": []},
        )

        redup_result = await run_tool(
            "redup",
            ["scan", str(repo_path), "--format", "json"],
            fallback={"duplication_groups": 0, "duplicated_lines": 0, "recoverable_lines": 0},
        )

        pyqual_result = await run_tool(
            "pyqual",
            ["check", str(repo_path), "--format", "json"],
            fallback={"passed": 0, "warnings": 0, "errors": 0, "score": 0},
        )

        health_score = calculate_health_score(stats, code2llm_result, redup_result, pyqual_result)
        recommendations = generate_recommendations(code2llm_result, redup_result, pyqual_result)

        report = {
            "status": "complete",
            "repo": repo,
            "completed": _utc_now_iso(),
            "stats": stats,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "metrics": {
                "complexity": code2llm_result,
                "duplication": redup_result,
                "quality": pyqual_result,
            },
            "recommendations": recommendations,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
            "files": code2llm_files.get("files", []),
        }

        # Save audit result to database
        save_audit_result(audit_id, report)

        weekly_issues = sum(
            1 for r in recommendations if r.get("priority") in ("high", "medium")
        )
        
        # Save badge cache to database
        save_badge_cache(repo, {
            "score": health_score,
            "grade": score_to_grade(health_score),
            "updated": _utc_now_iso(),
            "weekly_issues": weekly_issues,
        })

        # Add to scan history
        scan_entry = {
            "repo": repo,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "stats": stats,
            "completed": _utc_now_iso(),
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }

        # Persist to database
        try:
            save_scan(scan_entry)
        except Exception:
            pass

    except Exception as e:
        save_audit_result(audit_id, {
            "status": "error",
            "repo": repo,
            "error": str(e),
        })
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


async def _run_sandbox_analysis(audit_id: str, repo_url: str, repo: str):
    """Background analysis for sandbox mode (public repos only)."""
    workdir = Path(tempfile.mkdtemp(prefix="semcod-sandbox-"))

    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth=1",
            repo_url,
            str(workdir / "repo"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()

        if proc.returncode != 0:
            save_audit_result(audit_id, {
                "status": "error",
                "error": "Failed to clone repository. Ensure it's public.",
                "repo": repo,
            })
            return

        repo_path = workdir / "repo"
        stats = await count_code_stats(repo_path)

        code2llm_result = await run_tool(
            "code2llm",
            ["analyze", str(repo_path), "--format", "json"],
            fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0},
        )

        # Generate file contents for LLM prompts
        code2llm_files = await run_tool(
            "code2llm",
            [str(repo_path), "-f", "all", "--format", "json"],
            fallback={"files": []},
        )

        redup_result = await run_tool(
            "redup",
            ["scan", str(repo_path), "--format", "json"],
            fallback={"duplication_groups": 0, "duplicated_lines": 0, "recoverable_lines": 0},
        )

        pyqual_result = await run_tool(
            "pyqual",
            ["check", str(repo_path), "--format", "json"],
            fallback={"passed": 0, "warnings": 0, "errors": 0, "score": 0},
        )

        health_score = calculate_health_score(stats, code2llm_result, redup_result, pyqual_result)
        recommendations = generate_recommendations(code2llm_result, redup_result, pyqual_result)

        report = {
            "status": "complete",
            "repo": repo,
            "sandbox": True,
            "completed": _utc_now_iso(),
            "stats": stats,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "metrics": {
                "complexity": code2llm_result,
                "duplication": redup_result,
                "quality": pyqual_result,
            },
            "recommendations": recommendations,
            "files": code2llm_files.get("files", []),
        }

        # Save audit result to database
        save_audit_result(audit_id, report)

        # Add to scan history
        scan_entry = {
            "repo": repo,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "stats": stats,
            "completed": _utc_now_iso(),
            "sandbox": True,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }

        # Persist to database
        try:
            save_scan(scan_entry)
        except Exception:
            pass

    except Exception as e:
        save_audit_result(audit_id, {
            "status": "error",
            "error": str(e),
            "repo": repo,
        })
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
