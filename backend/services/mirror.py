"""Mirror service - clone and sync repos from GitHub/GitLab to local Gitea."""

import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import subprocess

import httpx

from adapters.github import GitHubAdapter
from adapters.gitlab import GitLabAdapter
from adapters.gitea import GiteaAdapter
from .mirror_models import MirrorConfig, MirrorStatus
from .mirror_workflow import generate_workflow

logger = logging.getLogger(__name__)


class MirrorService:
    """Service for mirroring repos to local Gitea."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        gitlab_token: Optional[str] = None,
        gitea_token: Optional[str] = None,
        gitea_url: str = "http://localhost:3000",
    ):
        self.github_token = github_token
        self.gitlab_token = gitlab_token
        self.gitea_token = gitea_token
        self.gitea_url = gitea_url

    async def create_mirror(
        self,
        config: MirrorConfig,
        user_id: Optional[int] = None,
    ) -> MirrorStatus:
        """Create new mirror by cloning source repo to Gitea.

        Flow:
        1. Clone source repo to temp directory
        2. Create target repo in Gitea
        3. Push to Gitea
        4. Setup CI/CD if auto_deploy enabled
        """
        mirror_id = f"{config.source_provider}_{config.source_repo.replace('/', '_')}"

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)

                # Get source adapter
                source_adapter = self._get_source_adapter(config.source_provider)
                target_adapter = GiteaAdapter(self.gitea_token, self.gitea_url)

                # Clone source repo
                source_url = await self._get_clone_url(
                    config.source_provider, config.source_repo
                )
                logger.info(f"[mirror] Cloning {source_url} to {tmpdir}")
                clone_result = subprocess.run(
                    ["git", "clone", source_url, str(tmp_path / "repo")],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if clone_result.returncode != 0:
                    raise Exception(f"Clone failed: {clone_result.stderr}")

                repo_path = tmp_path / "repo"

                # Get latest commit
                latest_commit = self._get_latest_commit(repo_path)

                # Create target repo in Gitea
                await self._create_gitea_repo(
                    target_adapter,
                    config.target_repo,
                    config.source_repo,
                )

                # Add Gitea remote
                gitea_url = await self._get_gitea_clone_url(config.target_repo)
                subprocess.run(
                    ["git", "remote", "add", "gitea", gitea_url],
                    cwd=repo_path,
                    capture_output=True,
                    check=True,
                )

                # Push to Gitea
                logger.info(f"[mirror] Pushing to Gitea: {config.target_repo}")
                push_result = subprocess.run(
                    ["git", "push", "-u", "gitea", "main"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if push_result.returncode != 0:
                    # Try master instead of main
                    push_result = subprocess.run(
                        ["git", "push", "-u", "gitea", "master"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )

                    if push_result.returncode != 0:
                        raise Exception(f"Push failed: {push_result.stderr}")

                # Setup CI/CD if auto_deploy enabled
                if config.auto_deploy:
                    await self._setup_ci_cd(repo_path, config, target_adapter)

                return MirrorStatus(
                    mirror_id=mirror_id,
                    status="success",
                    last_sync=datetime.now(timezone.utc).isoformat(),
                    last_commit=latest_commit,
                    commits_synced=1,
                )

        except Exception as e:
            logger.error(f"[mirror] Failed to create mirror: {e}")
            return MirrorStatus(
                mirror_id=mirror_id,
                status="failed",
                error=str(e),
            )

    async def sync_mirror(
        self,
        config: MirrorConfig,
    ) -> MirrorStatus:
        """Sync mirror by pulling latest changes from source and pushing to Gitea."""
        mirror_id = f"{config.source_provider}_{config.source_repo.replace('/', '_')}"

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)

                source_adapter = self._get_source_adapter(config.source_provider)
                target_adapter = GiteaAdapter(self.gitea_token, self.gitea_url)

                # Clone from Gitea (current state)
                gitea_url = await self._get_gitea_clone_url(config.target_repo)
                subprocess.run(
                    ["git", "clone", gitea_url, str(tmp_path / "repo")],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                repo_path = tmp_path / "repo"

                # Add source remote
                source_url = await self._get_clone_url(
                    config.source_provider, config.source_repo
                )
                subprocess.run(
                    ["git", "remote", "add", "source", source_url],
                    cwd=repo_path,
                    capture_output=True,
                    check=True,
                )

                # Fetch latest from source
                subprocess.run(
                    ["git", "fetch", "source"],
                    cwd=repo_path,
                    capture_output=True,
                    check=True,
                )

                # Get commit counts before merge
                commits_before = self._get_commit_count(repo_path)

                # Merge source changes
                subprocess.run(
                    ["git", "merge", "source/main"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                # If main doesn't exist, try master
                if (
                    subprocess.run(
                        ["git", "merge", "source/main"],
                        cwd=repo_path,
                        capture_output=True,
                    ).returncode
                    != 0
                ):
                    subprocess.run(
                        ["git", "merge", "source/master"],
                        cwd=repo_path,
                        capture_output=True,
                        check=True,
                    )

                # Get commit counts after merge
                commits_after = self._get_commit_count(repo_path)
                commits_synced = commits_after - commits_before

                # Get latest commit
                latest_commit = self._get_latest_commit(repo_path)

                # Push to Gitea
                subprocess.run(
                    ["git", "push", "gitea", "main"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if (
                    subprocess.run(
                        ["git", "push", "gitea", "main"],
                        cwd=repo_path,
                        capture_output=True,
                    ).returncode
                    != 0
                ):
                    subprocess.run(
                        ["git", "push", "gitea", "master"],
                        cwd=repo_path,
                        capture_output=True,
                        check=True,
                    )

                return MirrorStatus(
                    mirror_id=mirror_id,
                    status="success",
                    last_sync=datetime.now(timezone.utc).isoformat(),
                    last_commit=latest_commit,
                    commits_synced=commits_synced,
                )

        except Exception as e:
            logger.error(f"[mirror] Failed to sync: {e}")
            return MirrorStatus(
                mirror_id=mirror_id,
                status="failed",
                error=str(e),
            )

    async def _get_source_adapter(self, provider: str) -> Any:
        """Get adapter for source provider."""
        if provider == "github":
            return GitHubAdapter(self.github_token)
        elif provider == "gitlab":
            return GitLabAdapter(self.gitlab_token)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _get_clone_url(self, provider: str, repo: str) -> str:
        """Get clone URL for source repo."""
        if provider == "github":
            return f"https://github.com/{repo}.git"
        elif provider == "gitlab":
            return f"https://gitlab.com/{repo}.git"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _get_gitea_clone_url(self, repo: str) -> str:
        """Get clone URL for Gitea repo."""
        return f"http://gitea:gitea@{self.gitea_url.replace('http://', '').replace('https://', '')}/{repo}.git"

    async def _create_gitea_repo(
        self,
        adapter: GiteaAdapter,
        repo: str,
        source_repo: str,
    ) -> None:
        """Create repository in Gitea."""
        url = f"{adapter.api_base}/user/repos"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=adapter.get_api_headers(),
                json={
                    "name": repo.split("/")[1],
                    "description": f"Mirror of {source_repo}",
                    "private": False,
                    "auto_init": False,
                },
            )

        if resp.status_code not in (201, 409):  # 409 = already exists
            raise Exception(f"Failed to create Gitea repo: {resp.text}")

    async def _setup_ci_cd(
        self,
        repo_path: Path,
        config: MirrorConfig,
        adapter: GiteaAdapter,
    ) -> None:
        """Setup CI/CD pipeline in Gitea."""
        workflows_dir = repo_path / ".gitea" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create deployment workflow
        workflow_content = generate_workflow(config)
        (workflows_dir / "deploy.yml").write_text(workflow_content)

        # Commit and push CI/CD config
        subprocess.run(
            ["git", "add", ".gitea/workflows/deploy.yml"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "ci: add deployment workflow"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "push", "gitea", "main"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

    def _get_latest_commit(self, repo_path: Path) -> str:
        """Get latest commit SHA."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def _get_commit_count(self, repo_path: Path) -> int:
        """Get total commit count."""
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
