"""Marketplace API models."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PreviewRequest(BaseModel):
    repo: str
    provider: str = "github"


class PreviewResponse(BaseModel):
    score: int
    comment: str
    issues: List[Dict]
    suggested_patch: Optional[str] = None


class InstallRequest(BaseModel):
    repo: str
    provider: str
    apps: List[str]


class InstallResponse(BaseModel):
    status: str
    repo: str
    provider: str
    apps: List[str]
    webhook_url: Optional[str] = None


class AppStatusResponse(BaseModel):
    repo: str
    provider: str
    installed: bool
    apps: List[str]
    last_scan: Optional[str] = None
    score: Optional[int] = None


class AutoFixRequest(BaseModel):
    repo: str
    provider: str
    pr_id: int
    base_branch: str = "main"
    mirror_to_gitea: bool = False
    gitea_target_repo: Optional[str] = None
    auto_deploy: bool = False


class AutoFixResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
    pr_url: Optional[str] = None
    patches_generated: int = 0
