"""Marketplace Celery tasks - mirror sync and deployment."""

import asyncio
from typing import Dict, Any, Optional

try:
    from celery import shared_task
    from celery.exceptions import MaxRetriesExceededError

    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    from .._celery_stub import shared_task  # type: ignore[assignment]

from events.models import ProviderType


@shared_task(bind=True, max_retries=3)
def sync_mirror_task(
    self,
    mirror_id: str,
    source_repo: str,
    source_provider: str,
    target_repo: str,
    gitea_url: str = "http://localhost:3000",
    auto_deploy: bool = False,
    deploy_branch: str = "main",
    docker_image: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sync mirror from source to Gitea asynchronously.

    This task runs periodically to keep mirrors in sync.
    """
    try:
        from services.mirror import MirrorService, MirrorConfig

        # Get tokens
        github_token = _get_token_for_provider(ProviderType.GITHUB)
        gitlab_token = _get_token_for_provider(ProviderType.GITLAB)
        gitea_token = _get_token_for_provider(ProviderType.GITEA) or "gitea"

        # Create mirror service
        service = MirrorService(
            github_token=github_token,
            gitlab_token=gitlab_token,
            gitea_token=gitea_token,
            gitea_url=gitea_url,
        )

        # Create config
        config = MirrorConfig(
            source_repo=source_repo,
            source_provider=source_provider,
            target_repo=target_repo,
            gitea_url=gitea_url,
            auto_deploy=auto_deploy,
            deploy_branch=deploy_branch,
            docker_image=docker_image,
        )

        # Sync mirror
        result = asyncio.run(service.sync_mirror(config))

        return {
            "status": result.status,
            "mirror_id": mirror_id,
            "last_sync": result.last_sync,
            "last_commit": result.last_commit,
            "commits_synced": result.commits_synced,
            "error": result.error,
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            countdown = 60 * (2**self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        return {
            "status": "failed",
            "mirror_id": mirror_id,
            "error": str(exc),
        }


@shared_task
def schedule_periodic_mirrors() -> Dict[str, Any]:
    """
    Schedule periodic sync for all active mirrors.

    This should be called by Celery beat periodically.
    """
    from routers.mirror import _mirrors

    scheduled = []
    for mirror_id, mirror_info in _mirrors.items():
        if mirror_info["status"] == "success":
            task = sync_mirror_task.delay(
                mirror_id=mirror_id,
                source_repo=mirror_info["source_repo"],
                source_provider=mirror_info["source_provider"],
                target_repo=mirror_info["target_repo"],
                gitea_url=mirror_info["gitea_url"],
                auto_deploy=mirror_info["auto_deploy"],
                deploy_branch=mirror_info["deploy_branch"],
                docker_image=mirror_info["docker_image"],
            )
            scheduled.append(
                {
                    "mirror_id": mirror_id,
                    "task_id": task.id,
                }
            )

    return {
        "status": "scheduled",
        "count": len(scheduled),
        "mirrors": scheduled,
    }


def _get_token_for_provider(provider: ProviderType) -> str:
    """Get API token for provider from config."""
    import os

    token_map = {
        ProviderType.GITHUB: os.getenv(
            "GITHUB_TOKEN", os.getenv("GITHUB_CLIENT_SECRET", "")
        ),
        ProviderType.GITLAB: os.getenv("GITLAB_TOKEN", ""),
        ProviderType.GITEA: os.getenv("GITEA_TOKEN", ""),
    }
    return token_map.get(provider, "")
