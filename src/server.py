"""Main MCP server implementation."""

import asyncio
import click
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from prometheus_client import Counter, Histogram, start_http_server

from .config import get_settings
from .utils.logging import setup_logging, get_logger
from .storage.storage_manager import get_storage_manager
from .utils.validation import validate_path, validate_languages

logger = get_logger(__name__)

# Prometheus metrics
tool_calls = Counter("mcp_tool_calls", "MCP tool invocations", ["tool_name"])
tool_duration = Histogram("mcp_tool_duration", "Tool execution time", ["tool_name"])


class CodebaseIntelligenceMCP:
    """Codebase Intelligence MCP Server."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("codebase-intelligence")
        self.settings = get_settings()
        self.storage = get_storage_manager()
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="index_codebase",
                    description="Index a codebase directory for intelligent code analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to codebase directory"},
                            "languages": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Languages to index (python, javascript, typescript, java, go)",
                            },
                            "exclude_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Patterns to exclude (e.g., node_modules, *.test.ts)",
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="semantic_search",
                    description="Search code semantically by meaning, not just text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "language_filter": {"type": "string", "description": "Filter by language"},
                            "top_k": {"type": "integer", "description": "Number of results", "default": 10},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="analyze_dependencies",
                    description="Generate dependency graphs and detect circular dependencies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to analyze"},
                            "language": {"type": "string", "description": "Programming language"},
                            "depth": {"type": "integer", "description": "Max traversal depth", "default": 3},
                        },
                        "required": ["path", "language"],
                    },
                ),
                Tool(
                    name="compute_metrics",
                    description="Calculate code complexity and quality metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to file or directory"},
                        },
                        "required": ["file_path"],
                    },
                ),
                Tool(
                    name="detect_duplicates",
                    description="Find duplicate and similar code across the codebase",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to analyze"},
                            "similarity_threshold": {
                                "type": "number",
                                "description": "Similarity threshold (0-1)",
                                "default": 0.85,
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="generate_docs",
                    description="Auto-generate documentation from code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to document"},
                            "format": {
                                "type": "string",
                                "description": "Output format",
                                "enum": ["markdown", "html"],
                                "default": "markdown",
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="suggest_refactorings",
                    description="Get AI-powered refactoring suggestions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "File to analyze"},
                        },
                        "required": ["file_path"],
                    },
                ),
                Tool(
                    name="ask_codebase",
                    description="Query your codebase in natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Question about the codebase"},
                            "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                            "language_filter": {"type": "string", "description": "Filter by language"},
                        },
                        "required": ["question"],
                    },
                ),
                Tool(
                    name="get_call_graph",
                    description="Generate call graphs for functions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "function_name": {"type": "string", "description": "Function to analyze"},
                            "max_depth": {"type": "integer", "description": "Max depth", "default": 2},
                        },
                        "required": ["function_name"],
                    },
                ),
                Tool(
                    name="find_symbol",
                    description="Find symbol definitions and usages",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol_name": {"type": "string", "description": "Symbol to find"},
                            "symbol_type": {
                                "type": "string",
                                "description": "Symbol type",
                                "enum": ["function", "class", "variable"],
                            },
                        },
                        "required": ["symbol_name"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            tool_calls.labels(tool_name=name).inc()
            
            with tool_duration.labels(tool_name=name).time():
                try:
                    logger.info(f"Tool called: {name}", arguments=arguments)
                    
                    if name == "index_codebase":
                        result = await self._index_codebase(arguments)
                    elif name == "semantic_search":
                        result = await self._semantic_search(arguments)
                    elif name == "analyze_dependencies":
                        result = await self._analyze_dependencies(arguments)
                    elif name == "compute_metrics":
                        result = await self._compute_metrics(arguments)
                    elif name == "detect_duplicates":
                        result = await self._detect_duplicates(arguments)
                    elif name == "generate_docs":
                        result = await self._generate_docs(arguments)
                    elif name == "suggest_refactorings":
                        result = await self._suggest_refactorings(arguments)
                    elif name == "ask_codebase":
                        result = await self._ask_codebase(arguments)
                    elif name == "get_call_graph":
                        result = await self._get_call_graph(arguments)
                    elif name == "find_symbol":
                        result = await self._find_symbol(arguments)
                    else:
                        result = {"error": f"Unknown tool: {name}"}
                    
                    return [TextContent(type="text", text=str(result))]
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {name}", error=str(e))
                    return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _index_codebase(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Index a codebase directory."""
        # Import here to avoid circular imports
        from .tools.indexing_tools import IndexingTools
        
        indexer = IndexingTools(self.storage)
        return await indexer.index_codebase(
            path=args["path"],
            languages=args.get("languages"),
            exclude_patterns=args.get("exclude_patterns"),
        )

    async def _semantic_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search."""
        from .tools.search_tools import SearchTools
        
        searcher = SearchTools(self.storage)
        return await searcher.semantic_search(
            query=args["query"],
            language_filter=args.get("language_filter"),
            top_k=args.get("top_k", 10),
        )

    async def _analyze_dependencies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.analyze_dependencies(
            path=args["path"],
            language=args["language"],
            depth=args.get("depth", 3),
        )

    async def _compute_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compute code metrics."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.compute_metrics(file_path=args["file_path"])

    async def _detect_duplicates(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect duplicate code."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.detect_duplicates(
            path=args["path"],
            similarity_threshold=args.get("similarity_threshold", 0.85),
        )

    async def _generate_docs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.generate_docs(
            path=args["path"],
            format=args.get("format", "markdown"),
        )

    async def _suggest_refactorings(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest refactorings."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.suggest_refactorings(file_path=args["file_path"])

    async def _ask_codebase(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Answer questions about codebase."""
        from .tools.qa_tools import QATools
        
        qa = QATools(self.storage)
        return await qa.ask_codebase(
            question=args["question"],
            top_k=args.get("top_k", 5),
            language_filter=args.get("language_filter"),
        )

    async def _get_call_graph(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get call graph."""
        from .tools.analysis_tools import AnalysisTools
        
        analyzer = AnalysisTools(self.storage)
        return await analyzer.get_call_graph(
            function_name=args["function_name"],
            max_depth=args.get("max_depth", 2),
        )

    async def _find_symbol(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Find symbol."""
        from .tools.search_tools import SearchTools
        
        searcher = SearchTools(self.storage)
        return await searcher.find_symbol(
            symbol_name=args["symbol_name"],
            symbol_type=args.get("symbol_type"),
        )

    async def initialize(self) -> None:
        """Initialize storage and resources."""
        await self.storage.initialize()
        logger.info("MCP server initialized")

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.storage.close()
        logger.info("MCP server cleaned up")


async def run_stdio_server() -> None:
    """Run server in stdio mode."""
    logger.info("Starting MCP server in stdio mode")
    
    mcp = CodebaseIntelligenceMCP()
    await mcp.initialize()
    
    try:
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await mcp.server.run(
                read_stream,
                write_stream,
                mcp.server.create_initialization_options()
            )
    finally:
        await mcp.cleanup()


async def run_http_server(port: int) -> None:
    """Run server in HTTP mode."""
    logger.info(f"Starting MCP server in HTTP mode on port {port}")
    
    mcp = CodebaseIntelligenceMCP()
    await mcp.initialize()
    
    # Start Prometheus metrics server
    settings = get_settings()
    if settings.enable_metrics:
        start_http_server(9090)
        logger.info("Prometheus metrics available on :9090/metrics")
    
    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse
        
        async def health_check(request):
            """Health check endpoint."""
            health = await mcp.storage.health_check()
            status = all(health.values())
            return JSONResponse({
                "status": "healthy" if status else "unhealthy",
                "services": health
            })
        
        async def handle_sse(request):
            """Handle SSE connection."""
            async with SseServerTransport("/messages") as transport:
                await mcp.server.run(
                    transport.read_stream,
                    transport.write_stream,
                    mcp.server.create_initialization_options()
                )
        
        app = Starlette(
            routes=[
                Route("/health", health_check),
                Route("/sse", handle_sse),
            ]
        )
        
        import uvicorn
        await uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        ).serve()
        
    finally:
        await mcp.cleanup()


@click.command()
@click.option("--mode", type=click.Choice(["stdio", "http"]), default="stdio", help="Server mode")
@click.option("--port", type=int, default=10000, help="HTTP server port")
@click.option("--log-level", type=str, default="INFO", help="Logging level")
def main(mode: str, port: int, log_level: str) -> None:
    """Start the Codebase Intelligence MCP server."""
    setup_logging(log_level)
    
    if mode == "stdio":
        asyncio.run(run_stdio_server())
    else:
        asyncio.run(run_http_server(port))


if __name__ == "__main__":
    main()
