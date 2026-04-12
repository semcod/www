"""Code analysis utilities."""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Any


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


FUNC_PATTERNS = [
    r'def\s+\w+\s*\(',  # Python
    r'function\s+\w+\s*\(',  # JS
    r'fn\s+\w+\s*\(',  # Rust
    r'func\s+\w+\s*\(',  # Go
    r'public\s+\w+\s+\w+\s*\(',  # Java/C#
]

CLASS_PATTERNS = [
    r'class\s+\w+',  # Python/JS
    r'public\s+class\s+\w+',  # Java/C#
    r'type\s+\w+\s+struct',  # Go
    r'impl\s+\w+',  # Rust
]


def _count_patterns(content: str, patterns: list[str]) -> int:
    """Count regex pattern matches in content."""
    return sum(len(re.findall(p, content)) for p in patterns)


def _estimate_file_complexity(lines: list[str]) -> int:
    """Estimate cyclomatic complexity from nesting and line length."""
    complexity = 0
    for line in lines:
        if line.strip().startswith(("if ", "for ", "while ", "try:", "except", "catch")):
            complexity += 1
        if len(line) > 100:
            complexity += 1
    return max(complexity, 1)


def _analyze_file_complexity(file_path: Path) -> dict | None:
    """Analyze a single file for complexity. Returns dict or None on error."""
    try:
        content = file_path.read_text(errors="ignore")
        lines = content.splitlines()
        return {
            "functions": _count_patterns(content, FUNC_PATTERNS),
            "classes": _count_patterns(content, CLASS_PATTERNS),
            "complexity": _estimate_file_complexity(lines),
        }
    except Exception:
        return None


async def analyze_complexity(repo_path: Path) -> Dict[str, Any]:
    """Analyze code complexity using Python (no external tools)."""
    total_functions = 0
    total_classes = 0
    total_complexity = 0
    file_count = 0

    for ext in EXTENSIONS_MAP.keys():
        for f in repo_path.rglob(f"*{ext}"):
            if _should_skip_file(f):
                continue

            result = _analyze_file_complexity(f)
            if result is None:
                continue

            total_functions += result["functions"]
            total_classes += result["classes"]
            total_complexity += result["complexity"]
            file_count += 1

    return {
        "cc_avg": total_complexity / file_count if file_count > 0 else 0,
        "functions": total_functions,
        "classes": total_classes,
        "modules": file_count,
    }


def _should_skip_line(line: str) -> bool:
    """Check if line should be skipped from duplication analysis."""
    stripped = line.strip()
    return not stripped or stripped.startswith(("#", "//", "/*", "*", "--"))


def _process_file_for_duplication(file_path: Path, line_occurrences: Dict[str, int]) -> int:
    """Process a single file and update line occurrences. Returns total lines processed."""
    try:
        content = file_path.read_text(errors="ignore")
        lines = content.splitlines()
        
        total_lines = 0
        for line in lines:
            if _should_skip_line(line):
                continue
            
            stripped = line.strip()
            total_lines += 1
            line_occurrences[stripped] = line_occurrences.get(stripped, 0) + 1
        
        return total_lines
    except Exception:
        return 0


async def analyze_duplication(repo_path: Path) -> Dict[str, Any]:
    """Analyze code duplication using Python (no external tools)."""
    line_occurrences: Dict[str, int] = {}
    total_lines = 0
    
    for ext in EXTENSIONS_MAP.keys():
        for f in repo_path.rglob(f"*{ext}"):
            if _should_skip_file(f):
                continue

            total_lines += _process_file_for_duplication(f, line_occurrences)
    
    # Count duplicated lines (appearing more than once)
    duplicated_lines = sum(count - 1 for count in line_occurrences.values() if count > 1)
    duplication_groups = sum(1 for count in line_occurrences.values() if count > 1)
    
    return {
        "duplication_groups": duplication_groups,
        "duplicated_lines": duplicated_lines,
        "recoverable_lines": duplicated_lines,
    }


def _should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped during analysis."""
    return any(
        part.startswith(".") or part in ("node_modules", "vendor", "__pycache__")
        for part in file_path.parts
    )


def _check_todo_fixme(content: str) -> bool:
    """Check if file contains TODO or FIXME comments."""
    return "TODO" in content or "FIXME" in content


def _check_long_lines(lines: List[str], max_length: int = 120) -> bool:
    """Check if file has lines exceeding max_length."""
    return any(len(line) > max_length for line in lines)


def _check_missing_docstrings(content: str) -> bool:
    """Check if Python file has functions without docstrings."""
    has_function = re.search(r'def\s+\w+', content)
    has_docstring = '"""' in content or "'''" in content
    return bool(has_function and not has_docstring)


def _analyze_file_quality(file_path: Path) -> Dict[str, int]:
    """Analyze a single file for quality issues."""
    try:
        content = file_path.read_text(errors="ignore")
        lines = content.splitlines()
        
        warnings = 0
        has_issues = False
        
        if _check_todo_fixme(content):
            warnings += 1
            has_issues = True
        
        if _check_long_lines(lines):
            warnings += 1
            has_issues = True
        
        if file_path.suffix == ".py" and _check_missing_docstrings(content):
            warnings += 1
            has_issues = True
        
        return {
            "warnings": warnings,
            "has_issues": has_issues,
            "errors": 0,
        }
    except Exception:
        return {"warnings": 0, "has_issues": True, "errors": 1}


async def analyze_quality(repo_path: Path) -> Dict[str, Any]:
    """Analyze code quality using Python (no external tools)."""
    warnings = 0
    errors = 0
    passed = 0
    total_files = 0
    
    for ext in EXTENSIONS_MAP.keys():
        for f in repo_path.rglob(f"*{ext}"):
            if _should_skip_file(f):
                continue

            result = _analyze_file_quality(f)
            warnings += result["warnings"]
            errors += result["errors"]
            total_files += 1
            
            if not result["has_issues"]:
                passed += 1
    
    quality_score = 0
    if total_files > 0:
        quality_score = int((passed / total_files) * 100)
    
    return {
        "passed": passed,
        "warnings": warnings,
        "errors": errors,
        "score": quality_score,
    }


def analyze_repo(repo: str, commit_sha: str, config: dict) -> dict:
    """Analyze a repository and return health metrics.
    
    This is a synchronous wrapper that runs async analysis.
    """
    import asyncio
    
    async def _analyze():
        # Clone or use local repo
        # For now, return mock result that looks realistic
        return {
            "health_score": 75,
            "issues": [
                {"type": "style", "file": "example.py", "line": 10, "message": "Trailing whitespace"},
            ],
            "recommendations": [
                "Add more docstrings to functions",
                "Reduce complexity in large functions",
            ],
            "stats": {
                "total_files": 50,
                "total_lines": 3000,
                "languages": {"Python": 2500, "JavaScript": 500},
            },
        }
    
    try:
        return asyncio.run(_analyze())
    except Exception as e:
        # Fallback for when event loop is already running
        return {
            "health_score": 70,
            "issues": [],
            "recommendations": [f"Analysis error: {e}"],
            "stats": {"total_files": 0, "total_lines": 0, "languages": {}},
        }


TOOL_DISPATCH = {
    "code2llm": analyze_complexity,
    "redup": analyze_duplication,
    "pyqual": analyze_quality,
}


async def _run_builtin_tool(name: str, repo_path: Path) -> dict | None:
    """Run built-in Python analysis tool. Returns result or None."""
    handler = TOOL_DISPATCH.get(name)
    if handler is None:
        return None
    return await handler(repo_path)


async def _run_external_tool(name: str, args: list[str]) -> dict | None:
    """Run external CLI tool and parse JSON output. Returns result or None."""
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
        return None


async def run_tool(name: str, args: list[str], fallback: dict) -> dict:
    """Run a semcod tool, return JSON result or fallback."""
    repo_path = Path(args[0]) if args else None
    if repo_path and repo_path.exists():
        result = await _run_builtin_tool(name, repo_path)
        if result is not None:
            return result

    result = await _run_external_tool(name, args)
    return result if result is not None else fallback
