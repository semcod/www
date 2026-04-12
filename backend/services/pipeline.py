"""Shared analysis pipeline: clone → analyze → score → report.

Used by audit.py (_run_audit_pipeline, _run_sandbox_analysis) and
scheduler/scan_job.py (run_scheduled_scan) to avoid duplicating
the code2llm → redup → pyqual → score → recommendations pipeline.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from services.analyzer import count_code_stats, run_tool
from services.scoring import calculate_health_score, generate_recommendations, score_to_grade

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Structured result from an analysis pipeline run."""
    stats: dict = field(default_factory=dict)
    complexity: dict = field(default_factory=dict)
    duplication: dict = field(default_factory=dict)
    quality: dict = field(default_factory=dict)
    code2llm_files: dict = field(default_factory=dict)
    health_score: int = 0
    grade: str = "F"
    recommendations: list = field(default_factory=list)


async def _run_tools(repo_path: Path, *, include_code2llm_files: bool = False) -> PipelineResult:
    """Run code2llm + redup + pyqual on a cloned repo path.

    This is the core shared pipeline — no cloning, no persistence.
    """
    stats = await count_code_stats(repo_path)

    complexity = await run_tool(
        "code2llm",
        ["analyze", str(repo_path), "--format", "json"],
        fallback={"cc_avg": 0, "functions": 0, "classes": 0, "modules": 0},
    )
    duplication = await run_tool(
        "redup",
        ["scan", str(repo_path), "--format", "json"],
        fallback={"duplication_groups": 0, "duplicated_lines": 0, "recoverable_lines": 0},
    )
    quality = await run_tool(
        "pyqual",
        ["check", str(repo_path), "--format", "json"],
        fallback={"passed": 0, "warnings": 0, "errors": 0, "score": 0},
    )

    code2llm_files = {}
    if include_code2llm_files:
        code2llm_files = await run_tool(
            "code2llm",
            [str(repo_path), "-f", "all", "--format", "json"],
            fallback={"files": []},
        )

    health_score = calculate_health_score(stats, complexity, duplication, quality)
    recommendations = generate_recommendations(complexity, duplication, quality)

    return PipelineResult(
        stats=stats,
        complexity=complexity,
        duplication=duplication,
        quality=quality,
        code2llm_files=code2llm_files,
        health_score=health_score,
        grade=score_to_grade(health_score),
        recommendations=recommendations,
    )


async def clone_repo(repo: str, token: str, dest: Path) -> None:
    """Clone a GitHub repo (shallow) into *dest*. Raises on failure."""
    clone_url = (
        f"https://x-access-token:{token}@github.com/{repo}.git"
        if token
        else f"https://github.com/{repo}.git"
    )
    proc = await asyncio.create_subprocess_exec(
        "git", "clone", "--depth=1", clone_url, str(dest),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"git clone failed for {repo}")


async def run_pipeline(
    repo: str,
    token: str = "",
    *,
    include_code2llm_files: bool = False,
) -> PipelineResult:
    """Full pipeline: clone → analyze → score → report.

    Creates a temp dir, clones the repo, runs tools, cleans up.
    """
    workdir = Path(tempfile.mkdtemp(prefix="semcod-pipe-"))
    try:
        await clone_repo(repo, token, workdir / "repo")
        return await _run_tools(workdir / "repo", include_code2llm_files=include_code2llm_files)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


async def run_pipeline_local(
    repo_path: Path,
    *,
    include_code2llm_files: bool = False,
) -> PipelineResult:
    """Run tools on an already-cloned local path (no clone/cleanup)."""
    return await _run_tools(repo_path, include_code2llm_files=include_code2llm_files)
