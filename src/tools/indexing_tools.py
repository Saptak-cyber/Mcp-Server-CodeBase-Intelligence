"""Indexing tools for codebase."""

import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..storage.storage_manager import StorageManager
from ..utils.file_utils import FileUtils
from ..utils.logging import get_logger
from ..search.embeddings import EmbeddingGenerator
from ..search.chunker import CodeChunker
from ..parsers.tree_sitter_manager import TreeSitterManager

logger = get_logger(__name__)


class IndexingTools:
    """Tools for indexing codebases."""

    def __init__(self, storage: StorageManager):
        """Initialize indexing tools."""
        self.storage = storage
        self.embedder = EmbeddingGenerator()
        self.chunker = CodeChunker()
        self.parser = TreeSitterManager()

    async def _clone_repo(
        self, git_url: str, branch: Optional[str] = None
    ) -> str:
        """Clone a git repository to a temporary directory.
        
        Returns the path to the cloned directory.
        """
        tmp_dir = tempfile.mkdtemp(prefix="mcp_index_")
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

    async def index_codebase(
        self,
        path: Optional[str] = None,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
        languages: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Index a codebase directory or git repository."""
        start_time = time.time()
        stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "vectors_inserted": 0,
            "errors": 0,
        }
        cloned_dir = None

        try:
            # Resolve the path to index
            if git_url:
                cloned_dir = await self._clone_repo(git_url, branch)
                index_path = cloned_dir
                logger.info(f"Indexing cloned repo from {git_url}")
            elif path:
                index_path = path
            else:
                return {
                    "success": False,
                    "error": "Either 'path' or 'git_url' must be provided",
                    "stats": stats,
                }

            if not os.path.isdir(index_path):
                return {
                    "success": False,
                    "error": f"Directory not found: {index_path}",
                    "stats": stats,
                }

            logger.info(f"Starting indexing of {index_path}")

            # Default exclude patterns for cloned repos
            if cloned_dir and not exclude_patterns:
                exclude_patterns = [
                    "**/.git/**",
                    "**/__pycache__/**",
                    "**/node_modules/**",
                    "**/.venv/**",
                    "**/venv/**",
                ]
            elif cloned_dir and exclude_patterns:
                if "**/.git/**" not in exclude_patterns:
                    exclude_patterns.append("**/.git/**")

            # Scan directory for files
            file_count = 0
            all_chunks = []
            all_vectors = []
            all_payloads = []

            async for file_path, language in FileUtils.scan_directory(
                index_path, languages, exclude_patterns
            ):
                try:
                    # Read file
                    content = await FileUtils.read_file(file_path)

                    # Parse with tree-sitter
                    tree = await self.parser.parse(content, language)

                    # Chunk code
                    chunks = await self.chunker.chunk_code(content, tree, file_path, language)

                    if chunks:
                        # Generate embeddings
                        texts = [chunk["code"] for chunk in chunks]
                        vectors = await self.embedder.embed_batch(texts)

                        # Prepare payloads
                        payloads = [
                            {
                                "file_path": chunk["file_path"],
                                "language": chunk["language"],
                                "chunk_type": chunk["chunk_type"],
                                "name": chunk.get("name", ""),
                                "start_line": chunk["start_line"],
                                "end_line": chunk["end_line"],
                                "code": chunk["code"],
                            }
                            for chunk in chunks
                        ]

                        all_chunks.extend(chunks)
                        all_vectors.extend(vectors)
                        all_payloads.extend(payloads)

                        # Store file metadata
                        await self.storage.neon.upsert_file(
                            {
                                "path": file_path,
                                "language": language,
                                "size_bytes": len(content),
                                "last_modified": datetime.utcnow(),
                                "last_indexed": datetime.utcnow(),
                            }
                        )

                        stats["files_processed"] += 1
                        stats["chunks_created"] += len(chunks)

                except Exception as e:
                    logger.error(f"Error processing {file_path}", error=str(e))
                    stats["errors"] += 1

                file_count += 1

                # Batch insert to Qdrant
                if len(all_vectors) >= 100:
                    await self.storage.qdrant.insert_vectors(all_vectors, all_payloads)
                    stats["vectors_inserted"] += len(all_vectors)
                    all_vectors = []
                    all_payloads = []

            # Insert remaining vectors
            if all_vectors:
                await self.storage.qdrant.insert_vectors(all_vectors, all_payloads)
                stats["vectors_inserted"] += len(all_vectors)

            elapsed = time.time() - start_time
            stats["time_taken_seconds"] = int(round(elapsed, 2))
            stats["files_per_second"] = int(round(stats["files_processed"] / elapsed, 2))

            if git_url:
                stats["source"] = git_url

            logger.info("Indexing completed", stats=stats)
            return {"success": True, "stats": stats}

        except Exception as e:
            logger.error("Indexing failed", error=str(e))
            return {"success": False, "error": str(e), "stats": stats}

        finally:
            # Clean up cloned directory
            if cloned_dir and os.path.exists(cloned_dir):
                shutil.rmtree(cloned_dir, ignore_errors=True)
                logger.info("Cleaned up cloned repository")

