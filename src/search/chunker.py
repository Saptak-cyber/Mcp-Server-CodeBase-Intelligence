"""Code chunking for semantic search."""

from typing import List, Dict, Any
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CodeChunker:
    """Chunk code for embedding and search."""

    def __init__(self, max_chunk_size: int = 1000):
        """Initialize code chunker."""
        self.max_chunk_size = max_chunk_size

    async def chunk_code(
        self, code: str, tree: Any, file_path: str, language: str
    ) -> List[Dict[str, Any]]:
        """Chunk code at function/class boundaries."""
        chunks = []

        try:
            # Extract functions and classes from tree
            from ..parsers.tree_sitter_manager import TreeSitterManager

            parser = TreeSitterManager()
            functions = await parser.extract_functions(tree, language)
            classes = await parser.extract_classes(tree, language)

            # Create chunks for functions
            for func in functions:
                func_code = self._extract_code_segment(code, func["start_byte"], func["end_byte"])
                if func_code and len(func_code) <= self.max_chunk_size:
                    chunks.append(
                        {
                            "file_path": file_path,
                            "language": language,
                            "chunk_type": "function",
                            "name": func.get("name", "anonymous"),
                            "start_line": func["start_line"],
                            "end_line": func["end_line"],
                            "code": func_code,
                        }
                    )

            # Create chunks for classes
            for cls in classes:
                cls_code = self._extract_code_segment(code, cls["start_byte"], cls["end_byte"])
                if cls_code and len(cls_code) <= self.max_chunk_size:
                    chunks.append(
                        {
                            "file_path": file_path,
                            "language": language,
                            "chunk_type": "class",
                            "name": cls.get("name", "anonymous"),
                            "start_line": cls["start_line"],
                            "end_line": cls["end_line"],
                            "code": cls_code,
                        }
                    )

            # If no chunks, create file-level chunks
            if not chunks:
                chunks = self._chunk_by_lines(code, file_path, language)

        except Exception as e:
            logger.error("Chunking failed", error=str(e))
            # Fallback to line-based chunking
            chunks = self._chunk_by_lines(code, file_path, language)

        return chunks

    def _extract_code_segment(self, code: str, start_byte: int, end_byte: int) -> str:
        """Extract code segment by byte range."""
        try:
            return code[start_byte:end_byte]
        except Exception:
            return ""

    def _chunk_by_lines(self, code: str, file_path: str, language: str) -> List[Dict[str, Any]]:
        """Fallback: chunk code by line count."""
        lines = code.split("\n")
        chunks = []
        chunk_size = 50  # lines per chunk

        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i : i + chunk_size]
            chunk_code = "\n".join(chunk_lines)

            if chunk_code.strip():
                chunks.append(
                    {
                        "file_path": file_path,
                        "language": language,
                        "chunk_type": "file_segment",
                        "name": f"lines_{i+1}_{i+len(chunk_lines)}",
                        "start_line": i + 1,
                        "end_line": i + len(chunk_lines),
                        "code": chunk_code,
                    }
                )

        return chunks
