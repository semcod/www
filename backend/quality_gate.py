"""
Quality gate for semcod/www backend.

Rules (from refactoring-todo.toon.yaml TASK[5.1]):
  - new_file_max_lines: 400
  - new_function_max_cc: 12
  - cc_mean_delta_max: 0.2   (vs git HEAD baseline, skipped if no baseline)
  - critical_count_delta_max: 0  (functions with CC >= 15)

Usage:
  python quality_gate.py [--baseline <json>] [--save-baseline <json>]

Exit codes:
  0 — all checks passed
  1 — one or more violations found
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# ─── Config ───────────────────────────────────────────────────────────────────

MAX_FILE_LINES = 400
MAX_FUNCTION_CC = 12
CC_MEAN_DELTA_MAX = 0.2
CRITICAL_CC = 15

SCAN_DIRS = [Path(__file__).parent]
EXCLUDE_PATTERNS = {
    "__pycache__",
    ".venv",
    "node_modules",
    ".git",
    "dist",
    "migrations",
}


# ─── CC estimation (McCabe approximation via AST) ─────────────────────────────

CC_NODES = (
    ast.If,
    ast.For,
    ast.While,
    ast.ExceptHandler,
    ast.With,
    ast.Assert,
    ast.comprehension,
    ast.BoolOp,  # 'and'/'or' each add a branch
)


def _estimate_cc(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Estimate cyclomatic complexity of a function via AST node counting."""
    cc = 1
    for node in ast.walk(func_node):
        if isinstance(node, CC_NODES):
            if isinstance(node, ast.BoolOp):
                cc += len(node.values) - 1
            else:
                cc += 1
    return cc


# ─── File analysis ────────────────────────────────────────────────────────────


@dataclass
class FunctionResult:
    file: str
    name: str
    line: int
    cc: int


@dataclass
class FileResult:
    path: str
    lines: int
    functions: List[FunctionResult] = field(default_factory=list)

    @property
    def max_cc(self) -> int:
        return max((f.cc for f in self.functions), default=0)

    @property
    def mean_cc(self) -> float:
        if not self.functions:
            return 0.0
        return sum(f.cc for f in self.functions) / len(self.functions)


def _should_exclude(path: Path) -> bool:
    return any(p in path.parts for p in EXCLUDE_PATTERNS)


def analyze_file(path: Path) -> Optional[FileResult]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    lines = src.count("\n") + 1

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return FileResult(str(path), lines)

    result = FileResult(str(path), lines)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = _estimate_cc(node)
            result.functions.append(
                FunctionResult(str(path), node.name, node.lineno, cc)
            )

    return result


def collect_results(dirs: List[Path]) -> List[FileResult]:
    results = []
    for d in dirs:
        for py_file in sorted(d.rglob("*.py")):
            if _should_exclude(py_file):
                continue
            r = analyze_file(py_file)
            if r:
                results.append(r)
    return results


# ─── Gate checks ──────────────────────────────────────────────────────────────


@dataclass
class Violation:
    rule: str
    detail: str
    severity: str = "error"


def check_file_lines(
    results: List[FileResult], baseline: Optional[dict] = None
) -> List[Violation]:
    baseline_files: dict = (baseline or {}).get("oversized_files", {})
    violations = []
    for r in results:
        if r.lines <= MAX_FILE_LINES:
            continue
        prev = baseline_files.get(r.path)
        if prev is not None and r.lines <= prev:
            continue
        violations.append(
            Violation(
                "max_file_lines",
                f"{r.path}: {r.lines} lines (limit {MAX_FILE_LINES})",
            )
        )
    return violations


def check_function_cc(results: List[FileResult]) -> List[Violation]:
    violations = []
    for r in results:
        for f in r.functions:
            if f.cc > MAX_FUNCTION_CC:
                violations.append(
                    Violation(
                        "max_function_cc",
                        f"{f.file}:{f.line} {f.name}() CC={f.cc} (limit {MAX_FUNCTION_CC})",
                    )
                )
    return violations


def check_cc_mean_delta(
    results: List[FileResult], baseline: Optional[dict]
) -> List[Violation]:
    if not baseline:
        return []
    baseline_mean = baseline.get("cc_mean", 0.0)
    current_mean = _global_mean_cc(results)
    delta = current_mean - baseline_mean
    if delta > CC_MEAN_DELTA_MAX:
        return [
            Violation(
                "cc_mean_delta",
                f"CC mean rose {delta:+.2f} (baseline {baseline_mean:.2f} → current {current_mean:.2f}, limit +{CC_MEAN_DELTA_MAX})",
            )
        ]
    return []


def check_critical_delta(
    results: List[FileResult], baseline: Optional[dict]
) -> List[Violation]:
    if not baseline:
        return []
    baseline_critical = baseline.get("critical_count", 0)
    current_critical = sum(
        1 for r in results for f in r.functions if f.cc >= CRITICAL_CC
    )
    delta = current_critical - baseline_critical
    if delta > 0:
        return [
            Violation(
                "critical_count_delta",
                f"Critical functions (CC≥{CRITICAL_CC}) increased by {delta} ({baseline_critical} → {current_critical})",
            )
        ]
    return []


# ─── Metrics snapshot ─────────────────────────────────────────────────────────


def _global_mean_cc(results: List[FileResult]) -> float:
    all_ccs = [f.cc for r in results for f in r.functions]
    return sum(all_ccs) / len(all_ccs) if all_ccs else 0.0


def build_snapshot(results: List[FileResult]) -> dict:
    all_ccs = [f.cc for r in results for f in r.functions]
    critical = sum(1 for cc in all_ccs if cc >= CRITICAL_CC)
    oversized = {r.path: r.lines for r in results if r.lines > MAX_FILE_LINES}
    return {
        "files": len(results),
        "functions": len(all_ccs),
        "cc_mean": round(_global_mean_cc(results), 3),
        "cc_max": max(all_ccs, default=0),
        "critical_count": critical,
        "max_file_lines": max((r.lines for r in results), default=0),
        "oversized_files": oversized,
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────


def _parse_args() -> Tuple[Optional[Path], Optional[Path]]:
    baseline_path = None
    save_path = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--baseline" and i + 1 < len(args):
            baseline_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--save-baseline" and i + 1 < len(args):
            save_path = Path(args[i + 1])
            i += 2
        else:
            i += 1
    return baseline_path, save_path


def main() -> int:
    baseline_path, save_path = _parse_args()

    baseline: Optional[dict] = None
    if baseline_path and baseline_path.exists():
        try:
            baseline = json.loads(baseline_path.read_text())
        except (json.JSONDecodeError, OSError):
            print(f"[warn] Could not load baseline from {baseline_path}")

    print("=== Semcod Quality Gate ===")
    results = collect_results(SCAN_DIRS)
    snapshot = build_snapshot(results)

    print(f"  Files scanned : {snapshot['files']}")
    print(f"  Functions     : {snapshot['functions']}")
    print(f"  CC mean       : {snapshot['cc_mean']:.2f}")
    print(f"  CC max        : {snapshot['cc_max']}")
    print(f"  Critical (≥{CRITICAL_CC}) : {snapshot['critical_count']}")
    print(f"  Max file lines: {snapshot['max_file_lines']}")

    violations: List[Violation] = []
    violations += check_file_lines(results, baseline)
    violations += check_function_cc(results)
    violations += check_cc_mean_delta(results, baseline)
    violations += check_critical_delta(results, baseline)

    if save_path:
        save_path.write_text(json.dumps(snapshot, indent=2))
        print(f"\n  Baseline saved → {save_path}")

    if violations:
        print(f"\n❌ {len(violations)} violation(s):\n")
        for v in violations:
            print(f"  [{v.rule}] {v.detail}")
        print()
        return 1

    print("\n✅ All quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
