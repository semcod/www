"""Tests for auto-fix engine - patch generation and PR creation."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from services.autofix import PatchGenerator, AutoFixService, Patch, FixResult

pytestmark = [pytest.mark.fast, pytest.mark.unit]


class TestPatchGenerator:
    def test_trailing_whitespace_fix(self):
        generator = PatchGenerator()
        files = [{
            "filename": "test.py",
            "patch": """@@ -1,3 +1,3 @@
 line1   
-line2	
+line2
 line3
""",
        }]
        issues = [{"type": "style", "severity": "low"}]

        patches = generator.analyze_and_generate_patches(files, issues)

        assert len(patches) > 0
        assert patches[0].path == "test.py"
        assert "trailing whitespace" in patches[0].description.lower()

    def test_multiple_blank_lines_fix(self):
        generator = PatchGenerator()
        files = [{
            "filename": "test.py",
            "patch": """@@ -1,5 +1,3 @@
 line1
-
-
-
+\n
 line2
""",
        }]
        issues = [{"type": "style", "severity": "low"}]

        patches = generator.analyze_and_generate_patches(files, issues)

        # Should detect and fix multiple blank lines
        assert len(patches) > 0

    def test_no_fix_needed(self):
        generator = PatchGenerator()
        # Use a simple file with no trailing whitespace issues
        files = [{
            "filename": "clean.py",
            "patch": "",  # Empty patch = no changes
        }]
        issues = []

        patches = generator.analyze_and_generate_patches(files, issues)

        # No patch content = no patches generated
        assert len(patches) == 0

    def test_generate_fix_description(self):
        generator = PatchGenerator()
        patches = [
            Patch("file1.py", "old", "new", "Fix 1", "style"),
            Patch("file2.py", "old", "new", "Fix 2", "style"),
        ]

        desc = generator.generate_fix_description(patches)

        assert "2 file(s)" in desc
        assert "file1.py" in desc
        assert "file2.py" in desc
        # The title uses 🤖 emoji, not "Auto-fix" text
        assert "🤖" in desc or "Auto-Fix" in desc


class TestAutoFixService:
    @pytest.fixture
    def mock_adapter(self):
        adapter = MagicMock()
        adapter.get_ref_sha = AsyncMock(return_value="abc123")
        adapter.create_branch = AsyncMock(return_value="refs/heads/fix-branch")
        adapter.get_file_sha = AsyncMock(return_value=None)
        adapter.commit_file = AsyncMock(return_value="commit456")
        adapter.create_pr = AsyncMock(return_value="https://github.com/owner/repo/pull/42")
        adapter.delete_branch = AsyncMock(return_value=True)
        return adapter

    @pytest.mark.asyncio
    async def test_create_auto_fix_pr_success(self, mock_adapter):
        service = AutoFixService(mock_adapter, "token123")

        files = [{
            "filename": "test.py",
            "patch": """@@ -1,3 +1,3 @@
 line1   
-line2	
+line2
 line3
""",
        }]
        issues = [{"type": "style", "severity": "low"}]

        result = await service.create_auto_fix_pr(
            repo="owner/repo",
            base_branch="main",
            files=files,
            issues=issues,
            proposal_type="style_fix",
        )

        assert result.status == "success"
        assert result.patches_generated > 0
        assert result.patches_applied > 0
        assert result.branch is not None
        assert result.pr_url is not None
        assert "https://github.com" in result.pr_url

        # Verify adapter calls
        mock_adapter.get_ref_sha.assert_called_once_with("owner/repo", "main")
        mock_adapter.create_branch.assert_called_once()
        mock_adapter.commit_file.assert_called()
        mock_adapter.create_pr.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_fixes_needed(self, mock_adapter):
        service = AutoFixService(mock_adapter, "token123")

        # Clean files - no patch content = no changes to apply
        files = [{
            "filename": "clean.py",
            "patch": "",  # Empty patch = no changes
        }]
        issues = []

        result = await service.create_auto_fix_pr(
            repo="owner/repo",
            base_branch="main",
            files=files,
            issues=issues,
        )

        # Empty patches = no_fixes_needed
        assert result.status == "no_fixes_needed"
        assert result.patches_generated == 0
        assert result.patches_applied == 0

        # Should not create branch or PR
        mock_adapter.create_branch.assert_not_called()
        mock_adapter.create_pr.assert_not_called()

    @pytest.mark.asyncio
    async def test_partial_application(self, mock_adapter):
        service = AutoFixService(mock_adapter, "token123")

        # Make commit_file fail for some files
        mock_adapter.commit_file = AsyncMock(side_effect=[
            "commit1",
            Exception("Failed to commit"),
            "commit3",
        ])

        files = [
            {"filename": "file1.py", "patch": "@@ -1,1 +1,1 @@\n-old\n+new"},
            {"filename": "file2.py", "patch": "@@ -1,1 +1,1 @@\n-old\n+new"},
            {"filename": "file3.py", "patch": "@@ -1,1 +1,1 @@\n-old\n+new"},
        ]
        issues = [{"type": "style", "severity": "low"}]

        result = await service.create_auto_fix_pr(
            repo="owner/repo",
            base_branch="main",
            files=files,
            issues=issues,
        )

        assert result.status == "success"
        assert result.patches_applied >= 1

    @pytest.mark.asyncio
    async def test_all_patches_fail(self, mock_adapter):
        service = AutoFixService(mock_adapter, "token123")

        # Make all commits fail
        mock_adapter.commit_file = AsyncMock(side_effect=Exception("Failed"))

        files = [{"filename": "file.py", "patch": "@@ -1,1 +1,1 @@\n-old\n+new"}]
        issues = [{"type": "style", "severity": "low"}]

        result = await service.create_auto_fix_pr(
            repo="owner/repo",
            base_branch="main",
            files=files,
            issues=issues,
        )

        assert result.status == "failed"
        assert result.patches_applied == 0
        assert result.error is not None

        # Should clean up branch
        mock_adapter.delete_branch.assert_called_once()


class TestScoreImprovement:
    @pytest.mark.asyncio
    async def test_score_improved(self):
        service = AutoFixService(MagicMock(), "token")

        improved, message = await service.check_score_improvement(
            "owner/repo", 70, 85
        )

        assert improved is True
        assert "improved" in message.lower()
        assert "+15" in message

    @pytest.mark.asyncio
    async def test_score_regressed(self):
        service = AutoFixService(MagicMock(), "token")

        improved, message = await service.check_score_improvement(
            "owner/repo", 80, 60, threshold=-5
        )

        assert improved is False
        assert "regressed" in message.lower()

    @pytest.mark.asyncio
    async def test_score_maintained(self):
        service = AutoFixService(MagicMock(), "token")

        improved, message = await service.check_score_improvement(
            "owner/repo", 75, 75
        )

        assert improved is True  # Not worse
        assert "maintained" in message.lower()


class TestPatchPatterns:
    def test_fix_patterns_exist(self):
        generator = PatchGenerator()

        assert "trailing_whitespace" in generator.FIX_PATTERNS
        assert "multiple_blank_lines" in generator.FIX_PATTERNS
        assert "missing_final_newline" in generator.FIX_PATTERNS

    def test_trailing_whitespace_pattern(self):
        pattern = PatchGenerator.FIX_PATTERNS["trailing_whitespace"]

        import re
        test_line = "code   "
        match = re.search(pattern["pattern"], test_line)

        assert match is not None
