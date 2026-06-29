"""Base class for all Semcod marketplace apps."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AppResult:
    """Standard result format for all apps."""

    status: str  # success, warning, error, skipped
    score: Optional[int] = None  # 0-100 health score
    issues: List[Dict[str, Any]] = None
    recommendations: List[str] = None
    metrics: Dict[str, Any] = None
    actions_taken: List[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []
        if self.metrics is None:
            self.metrics = {}
        if self.actions_taken is None:
            self.actions_taken = []
        if self.details is None:
            self.details = {}


@dataclass
class AppContext:
    """Context passed to apps during execution."""

    repo: str
    event_type: str
    provider: str
    pr_id: Optional[int] = None
    branch: Optional[str] = None
    base_branch: Optional[str] = None
    diff: Optional[str] = None
    commit_sha: Optional[str] = None
    author: Optional[str] = None
    config: Dict[str, Any] = None
    raw_event: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.raw_event is None:
            self.raw_event = {}


class AppBase(ABC):
    """Base class for all marketplace apps.

    Apps must implement:
    - run_pipeline() - main analysis logic
    - get_triggers() - list of event types to subscribe to
    - get_actions() - list of actions app can perform

    Optionally override:
    - on_pr_opened(), on_push(), on_pr_comment() - specific handlers
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def run_pipeline(self, context: AppContext) -> AppResult:
        """Run main analysis pipeline.

        Args:
            context: Execution context with repo, diff, etc.

        Returns:
            AppResult with score, issues, recommendations
        """
        pass

    def get_triggers(self) -> List[str]:
        """Return list of event types this app responds to.

        Returns:
            List of: pull_request, push, pull_request_comment, issue
        """
        return ["pull_request"]

    def get_actions(self) -> List[str]:
        """Return list of actions this app can perform.

        Returns:
            List of: comment, create_pr, badge, label, approve
        """
        return ["comment"]

    def on_pr_opened(self, context: AppContext) -> AppResult:
        """Handle PR opened event. Default: run_pipeline."""
        return self.run_pipeline(context)

    def on_pr_synchronize(self, context: AppContext) -> AppResult:
        """Handle PR updated (new commits pushed). Default: run_pipeline."""
        return self.run_pipeline(context)

    def on_push(self, context: AppContext) -> AppResult:
        """Handle push to branch. Default: run_pipeline."""
        return self.run_pipeline(context)

    def on_pr_comment(self, context: AppContext, comment: str) -> AppResult:
        """Handle PR comment mentioning this app.

        Example: "@semcod-audit analyze this"
        """
        return AppResult(status="skipped", details={"reason": "not implemented"})

    def is_enabled_for_repo(self, repo: str) -> bool:
        """Check if app is enabled for specific repository."""
        enabled_repos = self.config.get("enabled_repos", [])
        if not enabled_repos:
            return True  # Enabled for all by default
        return repo in enabled_repos

    def get_pricing_tier(self) -> str:
        """Return pricing tier: free, pro, team, enterprise."""
        return self.config.get("pricing", "free")

    def can_execute(self, context: AppContext) -> bool:
        """Check if app can execute in current context (billing, permissions)."""
        # Check if enabled for this repo
        if not self.is_enabled_for_repo(context.repo):
            return False

        # Additional checks can be added here (billing, rate limits, etc.)
        return True
