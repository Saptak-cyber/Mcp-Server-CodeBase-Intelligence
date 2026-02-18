"""Dependency graph analysis using Neo4j."""

from typing import Dict, Any, List, Optional
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

    async def analyze(self, path: str, language: str, depth: int = 3) -> Dict[str, Any]:
        """Analyze dependencies for a codebase."""
        try:
            logger.info(f"Analyzing dependencies for {path}")

            # Scan files
            files_processed = 0
            dependencies = []
            total_functions = 0
            total_calls = 0

            async for file_path, file_lang in FileUtils.scan_directory(path, [language]):
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
                        dependencies.append({"from": file_path, "to": import_stmt})

                    # Extract function definitions and call relationships
                    functions, call_pairs = await self.parser.extract_function_calls(
                        tree, file_lang, file_path
                    )

                    # Create Function nodes
                    for func in functions:
                        await self._create_function_node(func)
                        total_functions += 1

                    # Create CALLS relationships
                    for call_pair in call_pairs:
                        await self._create_call_relationship(call_pair)
                        total_calls += 1

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
                "functions_found": total_functions,
                "call_relationships": total_calls,
                "circular_dependencies": circular_deps,
                "top_coupled_modules": coupling_scores[:10],
                "graph_visualization": self._generate_mermaid_graph(dependencies),
            }

        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_call_graph(
        self, function_name: str, max_depth: int = 2, project: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate call graph for a function."""
        try:
            # Build query with optional project filter
            if project:
                query = f"""
                MATCH path = (f:Function {{name: $name}})-[:CALLS*1..{max_depth}]->(called)
                WHERE any(r IN relationships(path) WHERE r.file_path IS NOT NULL)
                RETURN [n IN nodes(path) | {{name: n.name, file_path: n.file_path, start_line: n.start_line, end_line: n.end_line}}] as nodes,
                       [r IN relationships(path) | {{file_path: r.file_path, line: r.line}}] as rels
                LIMIT 100
                """
            else:
                query = f"""
                MATCH path = (f:Function {{name: $name}})-[:CALLS*1..{max_depth}]->(called)
                RETURN [n IN nodes(path) | {{name: n.name, file_path: n.file_path, start_line: n.start_line, end_line: n.end_line}}] as nodes,
                       [r IN relationships(path) | {{file_path: r.file_path, line: r.line}}] as rels
                LIMIT 100
                """

            results = await self.storage.neo4j.execute_query(query, {"name": function_name})

            # Format results into structured call chains
            call_graph: Dict[str, Any] = {"root": function_name, "calls": []}
            seen_edges: set = set()

            for result in results:
                nodes = result.get("nodes", [])
                rels = result.get("rels", [])
                for i, rel in enumerate(rels):
                    if i + 1 < len(nodes):
                        caller = nodes[i].get("name", "")
                        callee = nodes[i + 1].get("name", "")
                        edge_key = f"{caller}->{callee}"
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            call_graph["calls"].append({
                                "caller": caller,
                                "callee": callee,
                                "caller_file": nodes[i].get("file_path"),
                                "callee_file": nodes[i + 1].get("file_path"),
                                "line": rel.get("line"),
                            })

            return {
                "success": True,
                "function": function_name,
                "call_graph": call_graph,
                "visualization": self._generate_call_graph_mermaid(call_graph),
            }

        except Exception as e:
            logger.error("Call graph generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _create_file_node(self, file_path: str, language: str, size: int) -> None:
        """Create or update file node in Neo4j using MERGE to avoid duplicates."""
        await self.storage.neo4j.execute_query(
            """
            MERGE (f:File {path: $path})
            SET f.language = $language, f.size = $size
            """,
            {"path": file_path, "language": language, "size": size},
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

    async def _create_function_node(self, func: Dict[str, Any]) -> None:
        """Create Function node in Neo4j."""
        try:
            await self.storage.neo4j.execute_query(
                """
                MERGE (f:Function {name: $name, file_path: $file_path})
                SET f.start_line = $start_line, f.end_line = $end_line
                """,
                {
                    "name": func["name"],
                    "file_path": func["file_path"],
                    "start_line": func["start_line"],
                    "end_line": func["end_line"],
                },
            )
        except Exception as e:
            logger.warning(f"Failed to create function node: {func['name']}", error=str(e))

    async def _create_call_relationship(self, call_pair: Dict[str, Any]) -> None:
        """Create CALLS relationship between Function nodes."""
        try:
            # MERGE callee as a node too (it might be defined in another file)
            await self.storage.neo4j.execute_query(
                """
                MERGE (callee:Function {name: $callee_name})
                """,
                {"callee_name": call_pair["callee"]},
            )

            # Create the CALLS relationship
            await self.storage.neo4j.execute_query(
                """
                MATCH (caller:Function {name: $caller_name, file_path: $file_path})
                MATCH (callee:Function {name: $callee_name})
                MERGE (caller)-[:CALLS {file_path: $file_path, line: $line}]->(callee)
                """,
                {
                    "caller_name": call_pair["caller"],
                    "callee_name": call_pair["callee"],
                    "file_path": call_pair["file_path"],
                    "line": call_pair["line"],
                },
            )
        except Exception as e:
            logger.warning(
                f"Failed to create call relationship: {call_pair['caller']} -> {call_pair['callee']}",
                error=str(e),
            )

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

        for call in call_graph.get("calls", [])[:30]:
            if isinstance(call, dict):
                caller = self._sanitize_node_name(call.get("caller", ""))
                callee = self._sanitize_node_name(call.get("callee", ""))
                if caller and callee:
                    lines.append(f"    {caller} --> {callee}")

        return "\n".join(lines)

    def _sanitize_node_name(self, name: str) -> str:
        """Sanitize node name for Mermaid."""
        import os

        name = os.path.basename(name)
        name = name.replace(".", "_").replace("/", "_").replace("-", "_")
        return name[:50]
