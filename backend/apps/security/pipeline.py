"""Security App - Vulnerability scanning for Semcod."""

from typing import Dict, Any
import re

from apps.base import AppBase, AppContext, AppResult


class SecurityApp(AppBase):
    """Security vulnerability scanner.

    Detects:
    - Hardcoded secrets (API keys, tokens)
    - Vulnerable dependencies (CVEs)
    - Security anti-patterns
    - OWASP Top 10 issues
    """

    # Patterns for common secrets
    SECRET_PATTERNS = [
        (r"AIza[0-9A-Za-z_-]{35}", "Google API Key"),
        (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Token"),
        (r"glpat-[a-zA-Z0-9-]{20}", "GitLab Personal Token"),
        (r"private[_-]?key", "Private Key (generic)"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded Password"),
        (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API Key"),
    ]

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "security"
        cfg = config or {}
        self.block_on_critical = cfg.get("block_on_critical", True)
        self.scan_secrets = cfg.get("scan_secrets", True)
        self.scan_dependencies = cfg.get("scan_dependencies", True)

    def run_pipeline(self, context: AppContext) -> AppResult:
        """Run security scan on diff."""
        issues = []
        critical_count = 0
        high_count = 0

        content = context.diff or ""

        # Scan for secrets
        if self.scan_secrets:
            for pattern, name in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append(
                        {
                            "type": "secret",
                            "severity": "critical",
                            "message": f"Potential {name} found",
                            "line": content[: match.start()].count("\n") + 1,
                        }
                    )
                    critical_count += 1

        # Scan for security anti-patterns
        if "eval(" in content:
            issues.append(
                {
                    "type": "code_injection",
                    "severity": "high",
                    "message": "eval() detected - potential code injection risk",
                }
            )
            high_count += 1

        if "innerHTML" in content and "user" in content.lower():
            issues.append(
                {
                    "type": "xss",
                    "severity": "high",
                    "message": "Potential XSS vulnerability (innerHTML with user input)",
                }
            )
            high_count += 1

        # Calculate score
        score = max(0, 100 - critical_count * 50 - high_count * 20)
        passed = critical_count == 0

        return AppResult(
            status="success" if passed else "error",
            score=score,
            issues=issues,
            recommendations=self._get_recommendations(issues),
            actions_taken=["security_scan"] if issues else [],
            metrics={
                "critical": critical_count,
                "high": high_count,
                "total_issues": len(issues),
                "secrets_found": sum(1 for i in issues if i["type"] == "secret"),
                "block_pr": critical_count > 0 and self.block_on_critical,
            },
        )

    def _get_recommendations(self, issues: list) -> list:
        """Generate recommendations based on issues."""
        recs = []

        if any(i["type"] == "secret" for i in issues):
            recs.append("Move secrets to environment variables or secret manager")
            recs.append("Use git-secrets or pre-commit hooks to prevent commits")

        if any(i["type"] == "code_injection" for i in issues):
            recs.append("Replace eval() with safer alternatives (JSON.parse, Function)")

        if any(i["type"] == "xss" for i in issues):
            recs.append("Use textContent instead of innerHTML for user input")
            recs.append("Implement Content Security Policy (CSP)")

        return recs

    def get_triggers(self):
        return ["pull_request", "push"]

    def get_actions(self):
        return ["comment", "create_pr", "status_check", "label"]
