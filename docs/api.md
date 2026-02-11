# API Documentation

## MCP Tools

### 1. index_codebase

Index a codebase directory for intelligent analysis.

**Input Schema:**
```json
{
  "path": "string (required)",
  "languages": ["string"] (optional),
  "exclude_patterns": ["string"] (optional)
}
```

**Example:**
```json
{
  "path": "/path/to/project",
  "languages": ["python", "typescript"],
  "exclude_patterns": ["node_modules", "*.test.ts"]
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "files_processed": 150,
    "chunks_created": 450,
    "vectors_inserted": 450,
    "time_taken_seconds": 45.2,
    "files_per_second": 3.3
  }
}
```

---

### 2. semantic_search

Search code semantically by meaning.

**Input Schema:**
```json
{
  "query": "string (required)",
  "language_filter": "string (optional)",
  "top_k": "integer (optional, default: 10)"
}
```

**Example:**
```json
{
  "query": "authentication middleware",
  "language_filter": "typescript",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "authentication middleware",
  "results_count": 5,
  "results": [
    {
      "file_path": "src/middleware/auth.ts",
      "language": "typescript",
      "chunk_type": "function",
      "name": "authMiddleware",
      "lines": "15-42",
      "code": "export function authMiddleware(...) { ... }",
      "relevance_score": 0.9234
    }
  ]
}
```

---

### 3. analyze_dependencies

Generate dependency graphs and detect circular dependencies.

**Input Schema:**
```json
{
  "path": "string (required)",
  "language": "string (required)",
  "depth": "integer (optional, default: 3)"
}
```

**Example:**
```json
{
  "path": "/path/to/module",
  "language": "python",
  "depth": 3
}
```

**Response:**
```json
{
  "success": true,
  "files_processed": 45,
  "dependencies_found": 120,
  "circular_dependencies": [
    {"module1": "auth.py", "module2": "user.py"}
  ],
  "top_coupled_modules": [
    {"module": "utils.py", "coupling_score": 15}
  ],
  "graph_visualization": "graph TD\n  auth_py --> user_py\n  ..."
}
```

---

### 4. compute_metrics

Calculate code complexity and quality metrics.

**Input Schema:**
```json
{
  "file_path": "string (required)"
}
```

**Example:**
```json
{
  "file_path": "/path/to/file.py"
}
```

**Response:**
```json
{
  "success": true,
  "file_path": "/path/to/file.py",
  "metrics": {
    "maintainability_index": 75.3,
    "average_complexity": 4.2,
    "total_sloc": 150,
    "comment_lines": 45,
    "blank_lines": 20,
    "complexity_breakdown": [
      {
        "name": "process_data",
        "type": "function",
        "complexity": 8,
        "line": 25
      }
    ]
  }
}
```

---

### 5. detect_duplicates

Find duplicate and similar code.

**Input Schema:**
```json
{
  "path": "string (required)",
  "similarity_threshold": "number (optional, default: 0.85)"
}
```

**Example:**
```json
{
  "path": "/path/to/project",
  "similarity_threshold": 0.9
}
```

**Response:**
```json
{
  "success": true,
  "duplicate_groups_found": 3,
  "duplicates": [
    {
      "code_sample": "def validate_input(data)...",
      "instances": [
        {"file": "module_a.py", "lines": "10-15"},
        {"file": "module_b.py", "lines": "20-25"}
      ],
      "similarity_score": 0.95
    }
  ]
}
```

---

### 6. generate_docs

Auto-generate documentation from code.

**Input Schema:**
```json
{
  "path": "string (required)",
  "format": "string (optional, default: 'markdown')"
}
```

**Example:**
```json
{
  "path": "/path/to/module.py",
  "format": "markdown"
}
```

**Response:**
```json
{
  "success": true,
  "path": "/path/to/module.py",
  "format": "markdown",
  "documentation": "# Documentation for module.py\n\n## Functions\n..."
}
```

---

### 7. suggest_refactorings

Get AI-powered refactoring suggestions.

**Input Schema:**
```json
{
  "file_path": "string (required)"
}
```

**Example:**
```json
{
  "file_path": "/path/to/complex_file.py"
}
```

**Response:**
```json
{
  "success": true,
  "suggestions_count": 3,
  "suggestions": [
    {
      "type": "high_complexity",
      "entity": "process_data",
      "severity": "warning",
      "message": "Cyclomatic complexity of 15 is high. Consider breaking down..."
    }
  ]
}
```

---

### 8. ask_codebase

Query codebase in natural language.

**Input Schema:**
```json
{
  "question": "string (required)",
  "top_k": "integer (optional, default: 5)",
  "language_filter": "string (optional)"
}
```

**Example:**
```json
{
  "question": "How does user authentication work?",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "question": "How does user authentication work?",
  "contexts_retrieved": 5,
  "response": "Based on your question...",
  "relevant_code": [
    {
      "file_path": "auth/middleware.py",
      "code": "...",
      "relevance_score": 0.91
    }
  ]
}
```

---

### 9. get_call_graph

Generate call graphs for functions.

**Input Schema:**
```json
{
  "function_name": "string (required)",
  "max_depth": "integer (optional, default: 2)"
}
```

**Example:**
```json
{
  "function_name": "authenticate_user",
  "max_depth": 2
}
```

**Response:**
```json
{
  "success": true,
  "function": "authenticate_user",
  "call_graph": {
    "root": "authenticate_user",
    "calls": ["validate_token", "get_user"]
  },
  "visualization": "graph TD\n  authenticate_user --> validate_token\n  ..."
}
```

---

### 10. find_symbol

Find symbol definitions and usages.

**Input Schema:**
```json
{
  "symbol_name": "string (required)",
  "symbol_type": "string (optional)"
}
```

**Example:**
```json
{
  "symbol_name": "UserService",
  "symbol_type": "class"
}
```

**Response:**
```json
{
  "success": true,
  "symbol_name": "UserService",
  "found_count": 3,
  "locations": [
    {
      "file_path": "services/user.py",
      "type": "class",
      "lines": "10-50",
      "code": "class UserService..."
    }
  ]
}
```

## Error Handling

All tools return errors in a consistent format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

## Rate Limiting

- Semantic search: 100 requests/minute
- Indexing: 10 requests/hour
- Other tools: 200 requests/minute
