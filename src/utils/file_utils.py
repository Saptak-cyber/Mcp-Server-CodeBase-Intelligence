"""File utility functions."""

import os
import aiofiles
from pathlib import Path
from typing import List, Optional, AsyncIterator
from .logging import get_logger

logger = get_logger(__name__)


class FileUtils:
    """Utility class for file operations."""

    SUPPORTED_EXTENSIONS = {
        "python": [".py"],
        "javascript": [".js", ".jsx"],
        "typescript": [".ts", ".tsx"],
        "java": [".java"],
        "go": [".go"],
    }

    @staticmethod
    async def read_file(file_path: str) -> str:
        """Read file contents asynchronously."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Failed to read file: {file_path}", error=str(e))
            raise

    @staticmethod
    async def write_file(file_path: str, content: str) -> None:
        """Write content to file asynchronously."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file: {file_path}", error=str(e))
            raise

    @staticmethod
    def get_language_from_extension(file_path: str) -> Optional[str]:
        """Determine language from file extension."""
        ext = Path(file_path).suffix.lower()
        for language, extensions in FileUtils.SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return language
        return None

    @staticmethod
    async def scan_directory(
        directory: str,
        languages: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_file_size_mb: int = 10,
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Scan directory for source files.

        Yields:
            Tuple of (file_path, language)
        """
        exclude_patterns = exclude_patterns or [
            "node_modules",
            ".git",
            "__pycache__",
            "venv",
            "dist",
            "build",
        ]

        max_size = max_file_size_mb * 1024 * 1024

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not any(pattern in os.path.join(root, d) for pattern in exclude_patterns)
            ]

            for file in files:
                file_path = os.path.join(root, file)

                # Check file size
                try:
                    if os.path.getsize(file_path) > max_size:
                        logger.warning(f"Skipping large file: {file_path}")
                        continue
                except OSError:
                    continue

                # Check language
                language = FileUtils.get_language_from_extension(file_path)
                if language is None:
                    continue

                if languages and language not in languages:
                    continue

                # Check exclude patterns
                if any(pattern in file_path for pattern in exclude_patterns):
                    continue

                yield (file_path, language)

    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize file path."""
        return os.path.normpath(os.path.abspath(path))

    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """Get relative path from base."""
        return os.path.relpath(file_path, base_path)
