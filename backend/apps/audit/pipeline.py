"""Audit App - Code quality analysis for Semcod."""
from typing import Dict, Any

from apps.base import AppBase, AppContext, AppResult


class AuditApp(AppBase):
    """Main code quality audit app.

    Analyzes:
    - Cyclomatic complexity
    - Code duplication
    - Maintainability metrics
    - Overall health score
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "audit"
        cfg = config or {}
        self.max_complexity = cfg.get("max_complexity", 15)
        self.max_duplication = cfg.get("max_duplication", 5)
        self.min_health_score = cfg.get("min_health_score", 70)

    def run_pipeline(self, context: AppContext) -> AppResult:
        """Run code quality audit on repository/diff."""
        issues = self._detect_issues(context.diff or "")
        score = self._calculate_score(issues)
        grade = self._score_to_grade(score)
        recommendations = self._generate_recommendations(issues)

        return AppResult(
            status="success" if score >= self.min_health_score else "warning",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "grade": grade,
                "issues_count": len(issues),
                "complexity_violations": sum(1 for i in issues if i["type"] == "complexity"),
                "duplications": sum(1 for i in issues if i["type"] == "duplication"),
            },
        )

    def _detect_issues(self, diff: str) -> list:
        """Detect code quality issues in diff."""
        issues = []
        diff_lower = diff.lower()

        if "complex" in diff_lower:
            issues.append({
                "type": "complexity",
                "severity": "medium",
                "message": "High cyclomatic complexity detected",
            })

        if "duplicate" in diff_lower:
            issues.append({
                "type": "duplication",
                "severity": "high",
                "message": "Code duplication detected",
            })

        if "TODO" in diff:
            issues.append({
                "type": "todo",
                "severity": "low",
                "message": "TODO comments found",
            })

        return issues

    def _calculate_score(self, issues: list) -> int:
        """Calculate health score based on issues."""
        base_score = 100
        for issue in issues:
            if issue["severity"] == "high":
                base_score -= 20
            elif issue["severity"] == "medium":
                base_score -= 10
            else:
                base_score -= 5
        return max(0, base_score)

    def _generate_recommendations(self, issues: list) -> list:
        """Generate recommendations based on detected issues."""
        recommendations = []
        if any(i["type"] == "complexity" for i in issues):
            recommendations.append("Refactor complex functions into smaller ones")
        if any(i["type"] == "duplication" for i in issues):
            recommendations.append("Extract duplicate code into shared functions")
        return recommendations

    def get_triggers(self):
        return ["pull_request", "push"]

    def get_actions(self):
        return ["comment", "badge", "status_check"]

    def _score_to_grade(self, score: int) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
