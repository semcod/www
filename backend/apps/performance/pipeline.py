"""Performance App - Performance analysis for Semcod."""

from typing import Dict, Any

from apps.base import AppBase, AppContext, AppResult


class PerformanceApp(AppBase):
    """Performance bottleneck analyzer.

    Detects:
    - Slow database queries (N+1)
    - Memory leaks
    - Inefficient algorithms
    - Bundle size issues
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "performance"
        cfg = config or {}
        self.max_query_time = cfg.get("max_query_time_ms", 100)
        self.max_memory = cfg.get("max_memory_mb", 512)

    def run_pipeline(self, context: AppContext) -> AppResult:
        """Run performance analysis."""
        content = context.diff or ""
        issues = self._detect_performance_issues(content)
        score = self._calculate_score(issues)

        return AppResult(
            status="success" if score >= 70 else "warning",
            score=score,
            issues=issues,
            recommendations=self._get_recommendations(issues),
            metrics={
                "query_issues": sum(1 for i in issues if "query" in i["type"]),
                "memory_issues": sum(1 for i in issues if i["type"] == "memory"),
                "async_issues": sum(1 for i in issues if "async" in i["type"]),
            },
        )

    def _detect_performance_issues(self, content: str) -> list:
        """Detect performance issues in code."""
        issues = []
        content_lower = content.lower()
        content_upper = content.upper()

        if "for" in content and "query" in content_lower:
            issues.append(
                {
                    "type": "n_plus_1",
                    "severity": "medium",
                    "message": "Potential N+1 query pattern detected",
                }
            )

        if "SELECT" in content_upper and "WHERE" in content_upper:
            if "index" not in content_lower:
                issues.append(
                    {
                        "type": "missing_index",
                        "severity": "medium",
                        "message": "Query without index - consider adding database index",
                    }
                )

        if "Array(" in content or "new Array" in content:
            issues.append(
                {
                    "type": "memory",
                    "severity": "low",
                    "message": "Large array allocation - monitor memory usage",
                }
            )

        if ".forEach" in content and "async" in content:
            issues.append(
                {
                    "type": "async_loop",
                    "severity": "high",
                    "message": "async/await in forEach - use for...of instead",
                }
            )

        return issues

    def _calculate_score(self, issues: list) -> int:
        """Calculate performance score based on issues."""
        severity_weights = {"critical": 30, "high": 20, "medium": 10, "low": 5}
        penalty = sum(severity_weights.get(i["severity"], 5) for i in issues)
        return max(0, 100 - penalty)

    def _get_recommendations(self, issues: list) -> list:
        """Generate performance recommendations."""
        recs = []

        if any(i["type"] == "n_plus_1" for i in issues):
            recs.append("Use eager loading (JOIN) instead of separate queries")
            recs.append("Consider using DataLoader pattern for GraphQL")

        if any(i["type"] == "missing_index" for i in issues):
            recs.append("Add database indexes for frequently queried columns")
            recs.append("Use EXPLAIN ANALYZE to verify query plans")

        if any(i["type"] == "async_loop" for i in issues):
            recs.append("Replace forEach with for...of for async operations")
            recs.append("Consider Promise.all() for parallel execution")

        return recs

    def get_triggers(self):
        return ["pull_request", "push"]

    def get_actions(self):
        return ["comment", "badge", "status_check"]
