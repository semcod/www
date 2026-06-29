"""reDSL API client — calls the reDSL refactoring engine for real code transformations."""

import logging
from typing import Any

import httpx

from config import REDLS_URL

logger = logging.getLogger(__name__)


class RedslClient:
    """HTTP client for the reDSL refactoring engine."""

    def __init__(self, base_url: str = REDLS_URL):
        self.base_url = base_url.rstrip("/")

    async def analyze(
        self, project_path: str, project_toon: str | None = None
    ) -> dict[str, Any]:
        """Analyze a project — returns metrics and alerts."""
        payload: dict[str, Any] = {"project_dir": project_path}
        if project_toon:
            payload["project_toon"] = project_toon
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.base_url}/analyze", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def decide(self, project_path: str) -> list[dict[str, Any]]:
        """Evaluate DSL rules — returns decisions without execution."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/decide",
                json={"project_dir": project_path},
            )
            resp.raise_for_status()
            return resp.json().get("explanation", [])

    async def refactor(
        self,
        project_path: str,
        max_actions: int = 10,
        dry_run: bool = True,
        fmt: str = "json",
    ) -> dict[str, Any]:
        """Run refactoring on a project — returns decisions and applied changes."""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/refactor",
                json={
                    "project_path": project_path,
                    "max_actions": max_actions,
                    "dry_run": dry_run,
                    "format": fmt,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def batch_hybrid(
        self, semcod_root: str, max_changes: int = 30
    ) -> dict[str, Any]:
        """Hybrid quality refactoring (no LLM needed)."""
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(
                f"{self.base_url}/batch/hybrid",
                json={
                    "semcod_root": semcod_root,
                    "max_changes": max_changes,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def cycle(
        self,
        project_path: str,
        max_actions: int = 3,
        clear_history: bool = True,
        llm_model: str | None = None,
    ) -> dict[str, Any]:
        """Run a full refactoring cycle — actually modifies files on disk via LLM.

        Unlike refactor() which only returns a plan, this endpoint:
        1. Analyzes project metrics
        2. Evaluates DSL rules → decisions
        3. Calls LLM to generate code transformations
        4. Writes modified files to disk
        5. Returns report with proposals_applied and files_modified
        """
        payload: dict[str, Any] = {
            "project_dir": project_path,
            "max_actions": max_actions,
            "clear_history": clear_history,
        }
        if llm_model:
            payload["llm_model"] = llm_model
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{self.base_url}/cycle",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def clear_history(self, project_path: str) -> dict[str, Any]:
        """Clear decision history for a project — removes duplicate decision blocks."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.base_url}/history/clear",
                params={"project_dir": project_path},
            )
            resp.raise_for_status()
            return resp.json()

    async def health_score(self, project_path: str) -> dict[str, Any]:
        """Get unified health score — returns grade, score, dimensions."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/health",
                json={"project_dir": project_path, "format": "json"},
            )
            resp.raise_for_status()
            return resp.json()

    async def health(self) -> bool:
        """Check if reDSL engine is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False
