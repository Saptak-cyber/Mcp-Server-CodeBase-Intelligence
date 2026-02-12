"""Shared git utilities for cloning repos and deriving project names."""

import os
import re
import shutil
import subprocess
import tempfile
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Tuple
from .logging import get_logger

logger = get_logger(__name__)


def derive_project_name(git_url: Optional[str] = None, path: Optional[str] = None) -> str:
    """Derive a project name from git URL or local path.

    Priority: git_url repo name > path basename > 'unknown'
    """
    if git_url:
        name = git_url.rstrip("/").rstrip(".git").split("/")[-1]
        return re.sub(r'[^\w\-.]', '_', name)
    elif path:
        return os.path.basename(os.path.normpath(path))
    return "unknown"


async def clone_repo(git_url: str, branch: Optional[str] = None) -> str:
    """Clone a git repository to a temporary directory.

    Returns the path to the cloned directory. Caller is responsible for cleanup.
    """
    tmp_dir = tempfile.mkdtemp(prefix="mcp_clone_")
    logger.info(f"Cloning {git_url} into {tmp_dir}")

    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([git_url, tmp_dir])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise RuntimeError(f"git clone failed: {result.stderr.strip()}")

        logger.info(f"Successfully cloned {git_url}")
        return tmp_dir
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError("git clone timed out after 120 seconds")


@asynccontextmanager
async def clone_or_use_path(
    path: Optional[str] = None,
    git_url: Optional[str] = None,
    branch: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Context manager that yields a local path.

    If git_url is provided, clones the repo and yields the temp dir path,
    cleaning up on exit. If path is provided, yields it directly.
    Raises ValueError if neither is provided.
    """
    if not path and not git_url:
        raise ValueError("Either 'path' or 'git_url' must be provided")

    cloned_dir = None
    try:
        if git_url:
            cloned_dir = await clone_repo(git_url, branch)
            yield cloned_dir
        else:
            yield path  # type: ignore[misc]
    finally:
        if cloned_dir:
            shutil.rmtree(cloned_dir, ignore_errors=True)
            logger.info(f"Cleaned up cloned repo: {cloned_dir}")
