"""Analysis tools for code metrics and dependencies."""

from typing import Dict, Any, Optional
from ..storage.storage_manager import StorageManager
from ..analysis.dependency_graph import DependencyGraphAnalyzer
from ..metrics.calculator import MetricsCalculator
from ..similarity.detector import SimilarityDetector
from ..docs.generator import DocumentationGenerator
from ..refactor.analyzer import RefactoringAnalyzer
from ..utils.logging import get_logger
from ..utils.git_utils import clone_or_use_path

logger = get_logger(__name__)


class AnalysisTools:
    """Tools for code analysis."""

    def __init__(self, storage: StorageManager):
        """Initialize analysis tools."""
        self.storage = storage
        self.dependency_analyzer = DependencyGraphAnalyzer(storage)
        self.metrics_calculator = MetricsCalculator(storage)
        self.similarity_detector = SimilarityDetector(storage)
        self.doc_generator = DocumentationGenerator()
        self.refactor_analyzer = RefactoringAnalyzer(storage)

    async def analyze_dependencies(
        self,
        path: Optional[str] = None,
        language: str = "python",
        depth: int = 3,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze dependencies and create graph."""
        try:
            async with clone_or_use_path(path, git_url, branch) as resolved_path:
                return await self.dependency_analyzer.analyze(resolved_path, language, depth)
        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def compute_metrics(
        self,
        file_path: Optional[str] = None,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compute code metrics."""
        try:
            async with clone_or_use_path(file_path, git_url, branch) as resolved_path:
                return await self.metrics_calculator.compute(resolved_path)
        except Exception as e:
            logger.error("Metrics computation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def detect_duplicates(
        self,
        path: Optional[str] = None,
        similarity_threshold: float = 0.85,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Detect duplicate code."""
        try:
            async with clone_or_use_path(path, git_url, branch) as resolved_path:
                return await self.similarity_detector.detect_duplicates(
                    resolved_path, similarity_threshold
                )
        except Exception as e:
            logger.error("Duplicate detection failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def generate_docs(
        self,
        path: Optional[str] = None,
        format: str = "markdown",
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate documentation."""
        try:
            async with clone_or_use_path(path, git_url, branch) as resolved_path:
                return await self.doc_generator.generate(resolved_path, format)
        except Exception as e:
            logger.error("Documentation generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def suggest_refactorings(
        self,
        file_path: Optional[str] = None,
        git_url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest refactorings."""
        try:
            async with clone_or_use_path(file_path, git_url, branch) as resolved_path:
                return await self.refactor_analyzer.analyze(resolved_path)
        except Exception as e:
            logger.error("Refactoring analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_call_graph(
        self,
        function_name: str,
        max_depth: int = 2,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get call graph for a function."""
        try:
            return await self.dependency_analyzer.get_call_graph(function_name, max_depth, project)
        except Exception as e:
            logger.error("Call graph generation failed", error=str(e))
            return {"success": False, "error": str(e)}
