"""Code analysis utilities."""

import asyncio
import json
from pathlib import Path


EXTENSIONS_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".sh": "Shell",
}


async def count_code_stats(repo_path: Path) -> dict:
    """Count source files and lines."""
    total_files = 0
    total_lines = 0
    languages: dict[str, int] = {}

    for ext, lang in EXTENSIONS_MAP.items():
        for f in repo_path.rglob(f"*{ext}"):
            if any(
                part.startswith(".") or part in ("node_modules", "vendor")
                for part in f.parts
            ):
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


async def run_tool(name: str, args: list[str], fallback: dict) -> dict:
    """Run a semcod tool, return JSON result or fallback."""
    try:
        proc = await asyncio.create_subprocess_exec(
            name,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        return json.loads(stdout.decode())
    except Exception:
        return fallback
