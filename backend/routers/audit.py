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
from services.pipeline import run_pipeline, run_pipeline_local, clone_repo
from services.scoring import score_to_grade
from services.scan_service import save_scan, get_recent_scans, save_audit_result, get_audit_result, save_badge_cache, get_badge_cache
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

    benchmark_meta = {
        "case_id": body.get("case_id"),
        "source_type": body.get("source_type"),
        "change_type": body.get("change_type"),
        "baseline_detected": body.get("baseline_detected"),
        "benchmark_mode": body.get("benchmark_mode", False),
        "ticket_id": body.get("ticket_id"),
        "pr_reference": body.get("pr_reference"),
    }

    # Save initial audit status to database
    save_audit_result(audit_id, {
        "status": "running",
        "repo": repo,
        "started": _utc_now_iso(),
        **{k: v for k, v in benchmark_meta.items() if v is not None},
    })

    _schedule_background_task(_run_audit_pipeline(audit_id, repo, token))
    return {"audit_id": audit_id, "status": "running", **{k: v for k, v in benchmark_meta.items() if v is not None}}


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
    """Analyze any public repository by URL (sandbox mode). Supports file:// for local repos."""
    body = await request.json()
    repo_url = body.get("repo_url", "")
    sandbox = body.get("sandbox", False)

    if not repo_url:
        raise HTTPException(400, "repo_url required")

    # Initialize actual_repo_url (defaults to repo_url)
    actual_repo_url = repo_url

    # Support local:/ paths for mounted volume repositories
    if repo_url.startswith("local:/"):
        # Extract repo name from local path for audit_id
        import os
        path = repo_url.replace("local:/", "/local-repos/")
        repo_name = os.path.basename(path)
        owner = "local"
        repo = repo_name
        # Use the actual mounted path for git clone
        actual_repo_url = path
        audit_id = hashlib.sha256(
            f"local/{repo_name}-{_utc_now_iso()}".encode()
        ).hexdigest()[:12]
    elif repo_url.startswith("file://"):
        # Extract repo name from file path for audit_id
        import os
        path = repo_url.replace("file://", "")
        repo_name = os.path.basename(path.rstrip("/.git"))
        owner = "local"
        repo = repo_name
        actual_repo_url = path
        audit_id = hashlib.sha256(
            f"local/{repo_name}-{_utc_now_iso()}".encode()
        ).hexdigest()[:12]
    else:
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

    benchmark_meta = {
        "case_id": body.get("case_id"),
        "source_type": body.get("source_type"),
        "change_type": body.get("change_type"),
        "baseline_detected": body.get("baseline_detected"),
        "benchmark_mode": body.get("benchmark_mode", False),
        "ticket_id": body.get("ticket_id"),
        "pr_reference": body.get("pr_reference"),
    }

    # Save initial audit status to database
    save_audit_result(audit_id, {
        "status": "running",
        "repo": f"{owner}/{repo}",
        "sandbox": sandbox,
        "started": _utc_now_iso(),
        **{k: v for k, v in benchmark_meta.items() if v is not None},
    })

    # Use actual_repo_url for local repos, otherwise repo_url
    _schedule_background_task(_run_sandbox_analysis(audit_id, actual_repo_url, f"{owner}/{repo}"))
    return {"audit_id": audit_id, "status": "running", "sandbox": True, **{k: v for k, v in benchmark_meta.items() if v is not None}}


async def _run_audit_pipeline(audit_id: str, repo: str, token: str):
    """Background pipeline: clone → code2llm → redup → pyqual → report."""
    try:
        result = await run_pipeline(repo, token, include_code2llm_files=True)

        report = {
            "status": "complete",
            "repo": repo,
            "completed": _utc_now_iso(),
            "stats": result.stats,
            "health_score": result.health_score,
            "grade": result.grade,
            "metrics": {
                "complexity": result.complexity,
                "duplication": result.duplication,
                "quality": result.quality,
            },
            "recommendations": result.recommendations,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
            "files": result.code2llm_files.get("files", []),
        }

        save_audit_result(audit_id, report)

        weekly_issues = sum(1 for r in result.recommendations if r.get("priority") in ("high", "medium"))
        save_badge_cache(repo, {
            "score": result.health_score,
            "grade": result.grade,
            "updated": _utc_now_iso(),
            "weekly_issues": weekly_issues,
        })

        scan_entry = {
            "repo": repo,
            "health_score": result.health_score,
            "grade": result.grade,
            "stats": result.stats,
            "completed": _utc_now_iso(),
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }
        try:
            save_scan(scan_entry)
        except Exception:
            pass

    except Exception as e:
        save_audit_result(audit_id, {"status": "error", "repo": repo, "error": str(e)})


async def _run_sandbox_analysis(audit_id: str, repo_url: str, repo: str):
    """Background analysis for sandbox mode (public repos only)."""
    workdir = Path(tempfile.mkdtemp(prefix="semcod-sandbox-"))

    try:
        # Check if this is a local path (starts with /local-repos/)
        if repo_url.startswith("/local-repos/"):
            source_path = Path(repo_url)
            if source_path.exists():
                shutil.copytree(source_path, workdir / "repo")
            else:
                save_audit_result(audit_id, {
                    "status": "error",
                    "error": f"Local repository not found: {repo_url}",
                    "repo": repo,
                })
                return
        else:
            # Use git clone for remote repos
            proc = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth=1", repo_url, str(workdir / "repo"),
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

        result = await run_pipeline_local(workdir / "repo", include_code2llm_files=True)

        report = {
            "status": "complete",
            "repo": repo,
            "sandbox": True,
            "completed": _utc_now_iso(),
            "stats": result.stats,
            "health_score": result.health_score,
            "grade": result.grade,
            "metrics": {
                "complexity": result.complexity,
                "duplication": result.duplication,
                "quality": result.quality,
            },
            "recommendations": result.recommendations,
            "files": result.code2llm_files.get("files", []),
        }

        save_audit_result(audit_id, report)

        scan_entry = {
            "repo": repo,
            "health_score": result.health_score,
            "grade": result.grade,
            "stats": result.stats,
            "completed": _utc_now_iso(),
            "sandbox": True,
            "badge_url": f"{APP_URL}/badge/{repo.replace('/', '-')}.svg",
        }
        try:
            save_scan(scan_entry)
        except Exception:
            pass

    except Exception as e:
        save_audit_result(audit_id, {"status": "error", "error": str(e), "repo": repo})
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
