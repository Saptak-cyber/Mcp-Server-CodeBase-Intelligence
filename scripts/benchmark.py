"""Benchmark script for performance testing."""

import asyncio
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.storage_manager import get_storage_manager
from src.search.embeddings import EmbeddingGenerator
from src.parsers.tree_sitter_manager import TreeSitterManager


async def benchmark_embedding_generation():
    """Benchmark embedding generation."""
    print("\n=== Embedding Generation Benchmark ===")
    
    embedder = EmbeddingGenerator()
    
    texts = [
        "def hello(): pass",
        "class MyClass: pass",
        "import os",
    ] * 10  # 30 texts
    
    start = time.time()
    embeddings = await embedder.embed_batch(texts)
    elapsed = time.time() - start
    
    print(f"Generated {len(embeddings)} embeddings in {elapsed:.2f}s")
    print(f"Rate: {len(embeddings)/elapsed:.2f} embeddings/second")


async def benchmark_parsing():
    """Benchmark code parsing."""
    print("\n=== Parsing Benchmark ===")
    
    parser = TreeSitterManager()
    
    code = """
def function1():
    pass

def function2():
    pass

class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"""
    
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        tree = await parser.parse(code, "python")
        functions = await parser.extract_functions(tree, "python")
    
    elapsed = time.time() - start
    
    print(f"Parsed {iterations} files in {elapsed:.2f}s")
    print(f"Rate: {iterations/elapsed:.2f} files/second")


async def benchmark_storage():
    """Benchmark storage operations."""
    print("\n=== Storage Benchmark ===")
    
    storage = get_storage_manager()
    
    # Initialize
    print("Initializing storage...")
    start = time.time()
    await storage.initialize()
    elapsed = time.time() - start
    print(f"Storage initialized in {elapsed:.2f}s")
    
    # Health check
    print("\nRunning health checks...")
    health = await storage.health_check()
    for service, status in health.items():
        print(f"  {service}: {'✓' if status else '✗'}")
    
    await storage.close()


async def main():
    """Run all benchmarks."""
    print("Codebase Intelligence MCP Server - Performance Benchmarks")
    print("=" * 60)
    
    try:
        await benchmark_parsing()
        # await benchmark_embedding_generation()  # Requires API key
        # await benchmark_storage()  # Requires cloud credentials
        
        print("\n" + "=" * 60)
        print("Benchmarks complete!")
        
    except Exception as e:
        print(f"\nError running benchmarks: {e}")


if __name__ == "__main__":
    asyncio.run(main())
