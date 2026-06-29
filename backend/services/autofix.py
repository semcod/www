"""Auto-fix engine - generates patches and creates automated PRs with fixes."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Patch:
    """Represents a single file patch."""

    path: str
    original_content: str
    new_content: str
    description: str
    issue_type: str


@dataclass
class FixResult:
    """Result of applying auto-fix."""

    status: str  # success, partial, failed
    patches_generated: int
    patches_applied: int
    branch: Optional[str] = None
    pr_url: Optional[str] = None
    error: Optional[str] = None


class PatchGenerator:
    """Generates patches for common code issues."""

    # Issue patterns and their fixes
    FIX_PATTERNS = {
        "trailing_whitespace": {
            "pattern": r"[ \t]+$",
            "fix": "",
            "description": "Remove trailing whitespace",
        },
        "missing_final_newline": {
            "pattern": r"([^\n])$",
            "fix": r"\1\n",
            "description": "Add final newline",
        },
        "multiple_blank_lines": {
            "pattern": r"\n{3,}",
            "fix": "\n\n",
            "description": "Reduce multiple blank lines to two",
        },
        "todo_comment": {
            "pattern": r"#\s*TODO[:\s]*(.+)",
            "fix": None,  # Requires manual fix
            "description": "TODO comment found - manual review needed",
        },
    }

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def analyze_and_generate_patches(
        self, files: List[Dict[str, Any]], issues: List[Dict[str, Any]]
    ) -> List[Patch]:
        """Analyze files and generate patches for fixable issues."""
        patches = []

        for file_info in files:
            filename = file_info.get("filename", "")
            patch_content = file_info.get("patch", "")

            if not patch_content:
                continue

            # Parse the diff to get original content
            original_lines = self._parse_diff_original(patch_content)

            # Apply fixes based on issue type
            new_lines, applied_fixes = self._apply_fixes(
                original_lines, issues, filename
            )

            if applied_fixes and new_lines != original_lines:
                patches.append(
                    Patch(
                        path=filename,
                        original_content="\n".join(original_lines),
                        new_content="\n".join(new_lines),
                        description=f"Auto-fix: {', '.join(applied_fixes)}",
                        issue_type="auto_fix",
                    )
                )

        return patches

    def _parse_diff_original(self, diff_text: str) -> List[str]:
        """Extract original file content from diff."""
        lines = []
        for line in diff_text.split("\n"):
            if line.startswith("-") and not line.startswith("---"):
                lines.append(line[1:])
            elif not line.startswith("+") and not line.startswith("@@"):
                # Context line - appears in both
                if not line.startswith("---"):
                    lines.append(line)
        return lines

    def _apply_fixes(
        self, lines: List[str], issues: List[Dict], filename: str
    ) -> Tuple[List[str], List[str]]:
        """Apply automated fixes to lines. Returns (new_lines, fix_descriptions)."""
        new_lines = lines.copy()
        applied_fixes = []

        # Apply trailing whitespace fix
        trailing_ws_fixed = False
        for i, line in enumerate(new_lines):
            cleaned = re.sub(r"[ \t]+$", "", line)
            if cleaned != line:
                new_lines[i] = cleaned
                trailing_ws_fixed = True

        if trailing_ws_fixed:
            applied_fixes.append("remove trailing whitespace")

        # Fix multiple blank lines
        content = "\n".join(new_lines)
        original_content = content
        content = re.sub(r"\n{3,}", "\n\n", content)
        if content != original_content:
            applied_fixes.append("reduce multiple blank lines")
            new_lines = content.split("\n")

        # Ensure final newline
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"
            applied_fixes.append("add final newline")

        return new_lines, applied_fixes

    def generate_fix_description(self, patches: List[Patch]) -> str:
        """Generate PR description for auto-fix PR."""
        if not patches:
            return "No automated fixes available."

        desc_lines = [
            "## 🤖 Semcod Auto-Fix",
            "",
            f"This PR contains automated fixes for {len(patches)} file(s):",
            "",
        ]

        for patch in patches:
            desc_lines.append(f"- `{patch.path}`: {patch.description}")

        desc_lines.extend(
            [
                "",
                "### Changes Applied:",
                "- Code style fixes (trailing whitespace, blank lines)",
                "- Formatting improvements",
                "",
                "---",
                "*Generated automatically by [Semcod](https://semcod.com)*",
            ]
        )

        return "\n".join(desc_lines)


class AutoFixService:
    """Service for creating auto-fix PRs."""

    def __init__(self, adapter: Any, token: str):
        self.adapter = adapter
        self.token = token
        self.patch_generator = PatchGenerator()

    async def create_auto_fix_pr(
        self,
        repo: str,
        base_branch: str,
        files: List[Dict],
        issues: List[Dict],
        proposal_type: str = "auto_fix",
    ) -> FixResult:
        """Create automated PR with fixes.

        Flow:
        1. Generate patches from analysis
        2. Create new branch
        3. Apply patches as commits
        4. Create PR
        """
        try:
            # Generate patches
            patches = self.patch_generator.analyze_and_generate_patches(files, issues)

            if not patches:
                return FixResult(
                    status="no_fixes_needed",
                    patches_generated=0,
                    patches_applied=0,
                )

            # Get default branch SHA
            base_sha = await self.adapter.get_ref_sha(repo, base_branch)

            # Create fix branch
            fix_id = hashlib.sha256(
                f"{repo}-{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()[:8]
            branch = f"semcod-fix-{fix_id}"

            await self.adapter.create_branch(repo, branch, base_sha)

            # Apply each patch as a commit
            applied_count = 0
            for patch in patches:
                try:
                    # Get current file SHA (if exists)
                    file_sha = await self.adapter.get_file_sha(repo, patch.path, branch)

                    # Commit the fix
                    await self.adapter.commit_file(
                        repo=repo,
                        path=patch.path,
                        content=patch.new_content,
                        branch=branch,
                        message=f"fix({proposal_type}): {patch.description} [{fix_id}]",
                        token=self.token,
                        file_sha=file_sha,
                    )
                    applied_count += 1

                except Exception as e:
                    print(f"[autofix] Failed to apply patch to {patch.path}: {e}")
                    continue

            if applied_count == 0:
                # Clean up branch if no patches applied
                await self.adapter.delete_branch(repo, branch)
                return FixResult(
                    status="failed",
                    patches_generated=len(patches),
                    patches_applied=0,
                    error="No patches could be applied",
                )

            # Create PR
            pr_body = self.patch_generator.generate_fix_description(patches)
            pr_url = await self.adapter.create_pr(
                repo=repo,
                title=f"[Semcod] Auto-fix: {proposal_type.replace('_', ' ')} [{fix_id}]",
                body=pr_body,
                head_branch=branch,
                base_branch=base_branch,
            )

            return FixResult(
                status="success",
                patches_generated=len(patches),
                patches_applied=applied_count,
                branch=branch,
                pr_url=pr_url,
            )

        except Exception as e:
            return FixResult(
                status="failed",
                patches_generated=0,
                patches_applied=0,
                error=str(e),
            )

    async def check_score_improvement(
        self,
        repo: str,
        previous_score: int,
        new_score: int,
        threshold: int = -5,
    ) -> Tuple[bool, str]:
        """Check if auto-fix improved health score.

        Returns:
            (improved: bool, message: str)
        """
        delta = new_score - previous_score

        if delta < threshold:
            return False, f"Score regressed: {previous_score} → {new_score} (Δ{delta})"

        if delta > 0:
            return True, f"Score improved: {previous_score} → {new_score} (+{delta})"

        return True, f"Score maintained: {previous_score} → {new_score}"
