"""Base interface for git providers - PR Bot abstraction."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class GitProvider(ABC):
    """Abstract base class for git platform integrations.

    Provides unified interface for common operations across
    GitHub, GitLab, Gitea, and Bitbucket.
    """

    def __init__(self, token: str, base_url: Optional[str] = None):
        self.token = token
        self.base_url = base_url

    # ─── PR Operations ──────────────────────────────────────────────────────────

    @abstractmethod
    async def comment_on_pr(self, repo: str, pr_id: int, text: str) -> str:
        """Post a comment on a pull request. Returns comment URL."""
        pass

    @abstractmethod
    async def update_pr_description(self, repo: str, pr_id: int, description: str) -> bool:
        """Update PR description/body."""
        pass

    @abstractmethod
    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
    ) -> str:
        """Create a new pull request. Returns PR URL."""
        pass

    @abstractmethod
    async def close_pr(self, repo: str, pr_id: int, comment: Optional[str] = None) -> bool:
        """Close a pull request with optional comment."""
        pass

    # ─── Branch & Commit Operations ─────────────────────────────────────────────

    @abstractmethod
    async def create_branch(self, repo: str, branch: str, from_sha: str) -> str:
        """Create a new branch. Returns branch ref."""
        pass

    @abstractmethod
    async def delete_branch(self, repo: str, branch: str) -> bool:
        """Delete a branch."""
        pass

    @abstractmethod
    async def commit_file(
        self,
        repo: str,
        path: str,
        content: str,
        branch: str,
        message: str,
        file_sha: Optional[str] = None,
    ) -> str:
        """Commit a single file. Returns commit SHA."""
        pass

    @abstractmethod
    async def get_default_branch(self, repo: str) -> str:
        """Get repository default branch name."""
        pass

    @abstractmethod
    async def get_ref_sha(self, repo: str, ref: str) -> str:
        """Get SHA for a branch or tag ref."""
        pass

    @abstractmethod
    async def get_file_sha(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get SHA of existing file (for updates). None if file doesn't exist."""
        pass

    # ─── Diff & Content ─────────────────────────────────────────────────────────

    @abstractmethod
    async def get_pr_diff(self, repo: str, pr_id: int) -> str:
        """Get diff content of a pull request."""
        pass

    @abstractmethod
    async def get_file_content(self, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file content at specific ref."""
        pass

    # ─── Issue Operations ───────────────────────────────────────────────────────

    @abstractmethod
    async def create_issue(self, repo: str, title: str, body: str, labels: List[str]) -> str:
        """Create an issue. Returns issue URL."""
        pass

    @abstractmethod
    async def comment_on_issue(self, repo: str, issue_id: int, text: str) -> str:
        """Post a comment on an issue."""
        pass

    # ─── Check Runs / Status ────────────────────────────────────────────────────

    @abstractmethod
    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> str:
        """Create a check run (GitHub) or pipeline status (GitLab)."""
        pass

    @abstractmethod
    async def update_check_run(
        self,
        repo: str,
        check_run_id: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict] = None,
    ) -> bool:
        """Update an existing check run."""
        pass

    # ─── Webhook Verification ───────────────────────────────────────────────────

    @abstractmethod
    def verify_webhook_signature(self, body: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature from this provider."""
        pass

    # ─── Utility ───────────────────────────────────────────────────────────────

    @abstractmethod
    def get_api_headers(self) -> Dict[str, str]:
        """Get headers for API requests to this provider."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name identifier."""
        pass
