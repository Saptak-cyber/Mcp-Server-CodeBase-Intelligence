# MCP Tools Test Scripts

This directory contains test scripts for validating all MCP tools in the Codebase Intelligence server.

## Available Test Scripts

### 1. comprehensive_test.py ⭐ (Recommended)
The most complete test suite with timeout protection and detailed reporting.

```bash
./venv/bin/python scripts/comprehensive_test.py
```

**Features:**
- Tests all 10 MCP tools
- Timeout protection (10-20s per tool)
- Detailed progress output
- JSON results file
- Summary statistics
- Error categorization

**Output:** `comprehensive_test_results.json`

### 2. simple_test.py
Quick validation test for rapid feedback.

```bash
./venv/bin/python scripts/simple_test.py
```

**Features:**
- Tests 3 core tools
- 10s timeout per tool
- Minimal output
- Fast execution (~30s)

### 3. quick_test_mcp.py
Focused test on small scope for debugging.

```bash
./venv/bin/python scripts/quick_test_mcp.py
```

**Features:**
- Tests all tools on single file
- Detailed logging
- Good for debugging specific issues

**Output:** `quick_test_results.json`

### 4. test_mcp_tools.py
Full test suite with comprehensive logging.

```bash
./venv/bin/python scripts/test_mcp_tools.py
```

**Features:**
- Tests all tools on full codebase
- Very detailed logging
- Can be slow for large codebases

**Output:** `test_results.json`

## Test Results

All tests create JSON output files with detailed results:

```json
{
  "timestamp": "2026-02-12T20:00:39.003152",
  "summary": {
    "total": 10,
    "success": 10,
    "errors": 0,
    "timeouts": 0
  },
  "results": [...]
}
```

## Tools Tested

1. **index_codebase** - Index code for analysis
2. **semantic_search** - Search by meaning
3. **compute_metrics** - Calculate code metrics
4. **detect_duplicates** - Find duplicate code
5. **analyze_dependencies** - Dependency analysis
6. **generate_docs** - Auto-generate docs
7. **suggest_refactorings** - Refactoring suggestions
8. **ask_codebase** - Natural language queries
9. **get_call_graph** - Function call graphs
10. **find_symbol** - Symbol search

## Quick Start

```bash
# Run comprehensive test (recommended)
./venv/bin/python scripts/comprehensive_test.py

# Check results
cat comprehensive_test_results.json | jq '.summary'
```

## Troubleshooting

### Timeout Issues
If tests timeout, check:
- Database connections (Qdrant, Neo4j, Neon)
- Network connectivity
- Resource availability

### Connection Errors
Ensure all services are configured in `.env`:
- QDRANT_URL and QDRANT_API_KEY
- NEO4J_URI and NEO4J_PASSWORD
- NEON_DATABASE_URL
- HUGGINGFACE_API_KEY

### Import Errors
Make sure you're using the virtual environment:
```bash
source venv/bin/activate  # or ./venv/bin/python
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Test MCP Tools
  run: |
    ./venv/bin/python scripts/comprehensive_test.py
    if [ $? -ne 0 ]; then
      echo "MCP tools test failed"
      exit 1
    fi
```

## Performance Benchmarks

Typical execution times (on test file):
- compute_metrics: ~0.5s
- find_symbol: ~0.3s
- semantic_search: ~1.2s
- analyze_dependencies: ~0.5s
- generate_docs: ~0.3s
- suggest_refactorings: ~0.2s
- ask_codebase: ~1.5s
- get_call_graph: ~0.5s
- index_codebase: ~0.1s (single file)
- detect_duplicates: ~5s

Total: ~10-15 seconds for all tests

## Contributing

When adding new MCP tools:
1. Add test case to `comprehensive_test.py`
2. Update this README
3. Run full test suite
4. Update `MCP_TOOLS_TEST_SUMMARY.md`
