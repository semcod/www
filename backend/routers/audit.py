"""Audit endpoints and analysis pipeline."""

import asyncio
import hashlib
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from config import APP_URL
from services.analyzer import count_code_stats, run_tool
from services.scoring import calculate_health_score, generate_recommendations, score_to_grade
from store import audit_results, badge_cache

router = APIRouter()


@router.post("/api/audit")
async def run_audit(request: Request):
    """Run one-click audit on a repo. Body: { "repo": "owner/name", "token": "ghp_..." }"""
    body = await request.json()
    repo = body["repo"]
    token = body["token"]
    audit_id = hashlib.sha256(
        f"{repo}-{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12]

    audit_results[audit_id] = {
        "status": "running",
        "repo": repo,
        "started": datetime.utcnow().isoformat(),
    }

    asyncio.create_task(_run_audit_pipeline(audit_id, repo, token))
    return {"audit_id": audit_id, "status": "running"}


@router.get("/api/audit/{audit_id}")
async def get_audit_result(audit_id: str):
    """Poll audit status and results."""
    result = audit_results.get(audit_id)
    if not result:
        raise HTTPException(404, "Audit not found")
    return result


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
        f"{owner}/{repo}-{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12]

    audit_results[audit_id] = {
        "status": "running",
        "repo": f"{owner}/{repo}",
        "sandbox": sandbox,
        "started": datetime.utcnow().isoformat(),
    }

    asyncio.create_task(_run_sandbox_analysis(audit_id, repo_url, f"{owner}/{repo}"))
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
            "completed": datetime.utcnow().isoformat(),
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
        }

        audit_results[audit_id] = report

        weekly_issues = sum(
            1 for r in recommendations if r.get("priority") in ("high", "medium")
        )
        badge_cache[repo] = {
            "score": health_score,
            "grade": score_to_grade(health_score),
            "updated": datetime.utcnow().isoformat(),
            "weekly_issues": weekly_issues,
        }

    except Exception as e:
        audit_results[audit_id] = {
            "status": "error",
            "repo": repo,
            "error": str(e),
        }
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
            audit_results[audit_id] = {
                "status": "error",
                "error": "Failed to clone repository. Ensure it's public.",
                "repo": repo,
            }
            return

        repo_path = workdir / "repo"
        stats = await count_code_stats(repo_path)

        code2llm_result = await run_tool(
            "code2llm",
            ["analyze", str(repo_path), "--format", "json"],
            fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0},
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
            "completed": datetime.utcnow().isoformat(),
            "stats": stats,
            "health_score": health_score,
            "grade": score_to_grade(health_score),
            "metrics": {
                "complexity": code2llm_result,
                "duplication": redup_result,
                "quality": pyqual_result,
            },
            "recommendations": recommendations,
        }

        audit_results[audit_id] = report

    except Exception as e:
        audit_results[audit_id] = {
            "status": "error",
            "error": str(e),
            "repo": repo,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
