"""Mirror service models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MirrorConfig:
    """Configuration for repo mirror."""

    source_repo: str  # owner/repo
    source_provider: str  # github, gitlab
    target_repo: str  # owner/repo in Gitea
    gitea_url: str = "http://localhost:3000"
    sync_interval: int = 3600  # seconds
    auto_deploy: bool = False
    deploy_branch: str = "main"
    docker_image: Optional[str] = None


@dataclass
class MirrorStatus:
    """Status of mirror operation."""

    mirror_id: str
    status: str  # success, failed, in_progress
    last_sync: Optional[str] = None
    last_commit: Optional[str] = None
    error: Optional[str] = None
    commits_synced: int = 0
