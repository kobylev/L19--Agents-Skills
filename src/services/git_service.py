"""Git operations service wrapper."""

import shutil
from pathlib import Path
from typing import Optional

import git
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.logger import logger


class GitService:
    """Wrapper for Git operations."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def clone_repository(self, repo_url: str, target_dir: str, timeout: int = 60) -> bool:
        """
        Clone a Git repository.

        Args:
            repo_url: Repository URL
            target_dir: Target directory for cloning
            timeout: Timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Cloning {repo_url} to {target_dir}")

            # Remove existing directory if it exists
            target_path = Path(target_dir)
            if target_path.exists():
                shutil.rmtree(target_path)

            # Clone with shallow depth for speed
            git.Repo.clone_from(
                repo_url,
                target_dir,
                depth=1
            )

            logger.info(f"Successfully cloned: {repo_url}")
            return True

        except git.GitCommandError as e:
            logger.error(f"Git command failed for {repo_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Clone failed for {repo_url}: {e}")
            raise

    def cleanup_repository(self, target_dir: str):
        """
        Remove cloned repository.

        Args:
            target_dir: Directory to remove
        """
        try:
            target_path = Path(target_dir)
            if target_path.exists():
                shutil.rmtree(target_path)
                logger.debug(f"Cleaned up: {target_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {target_dir}: {e}")
