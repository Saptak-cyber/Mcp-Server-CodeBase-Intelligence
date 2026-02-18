"""Indexing tools for codebase."""

import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..storage.storage_manager import StorageManager
from ..utils.file_utils import FileUtils
from ..utils.logging import get_logger
from ..utils.git_utils import clone_or_use_path, derive_project_name
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

    async def index_codebase(
        self,
        path: Optional[str] = None,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
        project: Optional[str] = None,
        languages: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Index a codebase directory or git repository."""
        if not path and not git_url:
            return {
                "success": False,
                "error": "Either 'path' or 'git_url' must be provided",
                "stats": {},
            }

        start_time = time.time()
        stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "vectors_inserted": 0,
            "errors": 0,
        }

        try:
            async with clone_or_use_path(path, git_url, branch) as index_path:
                # Use provided project name
                project_name = project
                logger.info(f"Project name: {project_name}")

                if not os.path.isdir(index_path):
                    return {
                        "success": False,
                        "error": f"Directory not found: {index_path}",
                        "stats": stats,
                    }

                logger.info(f"Starting indexing of {index_path}")

                # Delete old vectors for this project before re-indexing (prevent duplicates)
                try:
                    await self.storage.qdrant.delete_by_filter({"project": project_name})
                    logger.info(f"Cleared old vectors for project: {project_name}")
                except Exception as e:
                    logger.warning(f"Could not clear old vectors", error=str(e))

                # Default exclude patterns for cloned repos
                if git_url and not exclude_patterns:
                    exclude_patterns = [
                        "**/.git/**",
                        "**/__pycache__/**",
                        "**/node_modules/**",
                        "**/.venv/**",
                        "**/venv/**",
                    ]
                elif git_url and exclude_patterns:
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
                            vectors, failed_indices = await self.embedder.embed_batch(texts)
                            
                            # Skip failed chunks
                            if failed_indices:
                                chunks = [c for i, c in enumerate(chunks) if i not in failed_indices]
                                logger.warning(f"Skipped {len(failed_indices)} chunks due to embedding failures")

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
                                    "project": project_name,
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
