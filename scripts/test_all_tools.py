#!/usr/bin/env python3
"""
Comprehensive test of all 10 MCP tools with detailed pass/fail reporting.
"""
import asyncio
import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import CodebaseIntelligenceMCP

results = {}

async def run_tool(name, mcp, handler, args):
    """Run a single tool and report results."""
    print(f"\n{'=' * 70}")
    print(f"  {name}")
    print(f"{'=' * 70}")
    start = time.time()
    try:
        result = await handler(args)
        elapsed = round(time.time() - start, 2)
        success = result.get("success", False)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  Status: {status}  ({elapsed}s)")
        if not success:
            print(f"  Error: {result.get('error', 'unknown')}")
        else:
            # Print key info
            for key in ["stats", "results_count", "found_count", "metrics", "circular_dependencies"]:
                if key in result:
                    val = result[key]
                    if isinstance(val, (dict, list)):
                        print(f"  {key}: {json.dumps(val, default=str)[:200]}")
                    else:
                        print(f"  {key}: {val}")
            # Show first few search results
            if result.get("results"):
                for i, r in enumerate(result["results"][:2], 1):
                    fp = r.get("file_path", r.get("path", "?"))
                    proj = r.get("project", "")
                    score = r.get("relevance_score", "")
                    extra = f" | project={proj}" if proj else ""
                    extra += f" | score={score}" if score else ""
                    print(f"    {i}. {fp}{extra}")
            if result.get("locations"):
                for i, loc in enumerate(result["locations"][:2], 1):
                    print(f"    {i}. {loc.get('file_path','?')} ({loc.get('type','?')})")
        results[name] = {"success": success, "time": elapsed, "error": result.get("error")}
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        print(f"  Status: 💥 ERROR  ({elapsed}s)")
        print(f"  Exception: {type(e).__name__}: {e}")
        results[name] = {"success": False, "time": elapsed, "error": str(e)}


async def main():
    print("=" * 70)
    print("  TESTING ALL 10 MCP TOOLS")
    print("=" * 70)

    mcp = CodebaseIntelligenceMCP()
    print("\nInitializing MCP Server...")
    await mcp.initialize()
    print("✅ Server initialized\n")

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_file = os.path.join(project_path, "src/server.py")

    try:
        # 1. index_codebase (with project param)
        await run_tool("1. index_codebase", mcp, mcp._index_codebase, {
            "path": project_path,
            "languages": ["python"],
            "exclude_patterns": ["venv", ".git", "__pycache__", "node_modules"],
            "project": "codebase-intelligence",
        })

        # 2. semantic_search (with project param)
        await run_tool("2. semantic_search", mcp, mcp._semantic_search, {
            "query": "storage manager initialization",
            "top_k": 5,
            "project": "codebase-intelligence",
        })

        # 3. analyze_dependencies
        await run_tool("3. analyze_dependencies", mcp, mcp._analyze_dependencies, {
            "path": server_file,
            "language": "python",
            "depth": 2,
        })

        # 4. compute_metrics
        await run_tool("4. compute_metrics", mcp, mcp._compute_metrics, {
            "file_path": server_file,
        })

        # 5. detect_duplicates
        await run_tool("5. detect_duplicates", mcp, mcp._detect_duplicates, {
            "path": os.path.join(project_path, "src"),
            "similarity_threshold": 0.85,
        })

        # 6. generate_docs
        await run_tool("6. generate_docs", mcp, mcp._generate_docs, {
            "path": server_file,
            "format": "markdown",
        })

        # 7. suggest_refactorings
        await run_tool("7. suggest_refactorings", mcp, mcp._suggest_refactorings, {
            "file_path": server_file,
        })

        # 8. ask_codebase (with project param)
        await run_tool("8. ask_codebase", mcp, mcp._ask_codebase, {
            "question": "How does the MCP server handle tool calls?",
            "top_k": 3,
            "project": "codebase-intelligence",
        })

        # 9. get_call_graph
        await run_tool("9. get_call_graph", mcp, mcp._get_call_graph, {
            "function_name": "initialize",
            "max_depth": 2,
        })

        # 10. find_symbol (with project param)
        await run_tool("10. find_symbol", mcp, mcp._find_symbol, {
            "symbol_name": "StorageManager",
            "symbol_type": "class",
            "project": "codebase-intelligence",
        })

    except Exception as e:
        print(f"\n💥 Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp.cleanup()

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    for name, r in results.items():
        icon = "✅" if r["success"] else "❌"
        err = f"  — {r['error']}" if r.get("error") else ""
        print(f"  {icon} {name}  ({r['time']}s){err}")
    print(f"\n  Result: {passed}/{total} tools passed")
    print("=" * 70)

    # Save results
    with open(os.path.join(project_path, "test_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed results saved to test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
