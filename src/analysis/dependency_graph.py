"""Dependency graph analysis using Neo4j."""

from typing import Dict, Any, List
from ..storage.storage_manager import StorageManager
from ..parsers.tree_sitter_manager import TreeSitterManager
from ..utils.file_utils import FileUtils
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DependencyGraphAnalyzer:
    """Analyze code dependencies using Neo4j graph database."""

    def __init__(self, storage: StorageManager):
        """Initialize dependency analyzer."""
        self.storage = storage
        self.parser = TreeSitterManager()

    async def analyze(
        self, path: str, language: str, depth: int = 3
    ) -> Dict[str, Any]:
        """Analyze dependencies for a codebase."""
        try:
            logger.info(f"Analyzing dependencies for {path}")

            # Scan files
            files_processed = 0
            dependencies = []

            async for file_path, file_lang in FileUtils.scan_directory(
                path, [language]
            ):
                try:
                    # Read and parse file
                    content = await FileUtils.read_file(file_path)
                    tree = await self.parser.parse(content, file_lang)

                    # Extract imports
                    imports = await self.parser.extract_imports(tree, file_lang)

                    # Create nodes in Neo4j
                    await self._create_file_node(file_path, file_lang, len(content))

                    # Create dependency relationships
                    for import_stmt in imports:
                        await self._create_dependency(file_path, import_stmt)
                        dependencies.append(
                            {"from": file_path, "to": import_stmt}
                        )

                    files_processed += 1

                except Exception as e:
                    logger.error(f"Error analyzing {file_path}", error=str(e))

            # Find circular dependencies
            circular_deps = await self.storage.neo4j.find_circular_dependencies()

            # Calculate module coupling
            coupling_scores = await self.storage.neo4j.calculate_module_coupling()

            return {
                "success": True,
                "files_processed": files_processed,
                "dependencies_found": len(dependencies),
                "circular_dependencies": circular_deps,
                "top_coupled_modules": coupling_scores[:10],
                "graph_visualization": self._generate_mermaid_graph(dependencies),
            }

        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_call_graph(
        self, function_name: str, max_depth: int = 2
    ) -> Dict[str, Any]:
        """Generate call graph for a function."""
        try:
            # Query Neo4j for function calls
            query = f"""
            MATCH path = (f:Function {{name: $name}})-[:CALLS*1..{max_depth}]->(called)
            RETURN path
            LIMIT 100
            """

            results = await self.storage.neo4j.execute_query(
                query, {"name": function_name}
            )

            # Format results
            call_graph = {"root": function_name, "calls": []}

            for result in results:
                path = result.get("path")
                if path:
                    call_graph["calls"].append(self._format_path(path))

            return {
                "success": True,
                "function": function_name,
                "call_graph": call_graph,
                "visualization": self._generate_call_graph_mermaid(call_graph),
            }

        except Exception as e:
            logger.error("Call graph generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _create_file_node(
        self, file_path: str, language: str, size: int
    ) -> None:
        """Create file node in Neo4j."""
        await self.storage.neo4j.create_node(
            "File",
            {
                "path": file_path,
                "language": language,
                "size": size,
            },
        )

    async def _create_dependency(self, from_file: str, to_module: str) -> None:
        """Create dependency relationship."""
        try:
            # Create module node if doesn't exist
            await self.storage.neo4j.execute_query(
                """
                MERGE (m:Module {name: $name})
                """,
                {"name": to_module},
            )

            # Create relationship
            await self.storage.neo4j.execute_query(
                """
                MATCH (f:File {path: $from_file})
                MATCH (m:Module {name: $to_module})
                MERGE (f)-[:DEPENDS_ON]->(m)
                """,
                {"from_file": from_file, "to_module": to_module},
            )
        except Exception as e:
            logger.warning("Failed to create dependency", error=str(e))

    def _generate_mermaid_graph(self, dependencies: List[Dict[str, str]]) -> str:
        """Generate Mermaid diagram for dependencies."""
        lines = ["graph TD"]
        
        # Limit to first 20 dependencies for readability
        for dep in dependencies[:20]:
            from_node = self._sanitize_node_name(dep["from"])
            to_node = self._sanitize_node_name(dep["to"])
            lines.append(f"    {from_node} --> {to_node}")

        return "\n".join(lines)

    def _generate_call_graph_mermaid(self, call_graph: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for call graph."""
        lines = ["graph TD"]
        root = self._sanitize_node_name(call_graph["root"])
        
        for call in call_graph.get("calls", [])[:20]:
            if isinstance(call, str):
                target = self._sanitize_node_name(call)
                lines.append(f"    {root} --> {target}")

        return "\n".join(lines)

    def _sanitize_node_name(self, name: str) -> str:
        """Sanitize node name for Mermaid."""
        # Remove special characters and paths
        import os
        name = os.path.basename(name)
        name = name.replace(".", "_").replace("/", "_").replace("-", "_")
        return name[:50]  # Limit length

    def _format_path(self, path: Any) -> str:
        """Format Neo4j path result."""
        # Simplified formatting
        return str(path)
