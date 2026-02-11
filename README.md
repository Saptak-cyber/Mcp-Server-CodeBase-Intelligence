# Codebase Intelligence MCP Server

A production-grade Model Context Protocol (MCP) server providing advanced code intelligence capabilities across multiple programming languages. Built with cloud-native architecture integrating 6 managed services for scalability and reliability.

## Features

- 🔍 **Semantic Code Search** - Vector-based search across 100k+ files using Qdrant Cloud
- 🕸️ **Dependency Analysis** - Graph-based dependency tracking with Neo4j Cloud
- 📊 **Code Metrics** - Cyclomatic complexity, maintainability index, and more
- 🔄 **Duplicate Detection** - AST and semantic-based code clone detection
- 📝 **Auto-Documentation** - Generate API documentation from code
- 🎯 **Refactoring Suggestions** - AI-powered code improvement recommendations
- 💬 **Natural Language Q&A** - Ask questions about your codebase in plain English
- 🌳 **Call Graph Analysis** - Visualize function call relationships

## Supported Languages

- JavaScript/TypeScript
- Python
- Java
- Go

## Architecture

The system integrates 6 cloud services for production-grade performance:

- **Qdrant Cloud** - Vector search for semantic code queries
- **Neo4j AuraDB** - Graph database for dependency analysis
- **Neon PostgreSQL** - Serverless database for metadata and metrics
- **Upstash Redis** - Distributed caching layer
- **HuggingFace Inference API** - Code embeddings generation
- **Render** - Deployment platform with auto-scaling

## Quick Start

### Prerequisites

- Python 3.11+
- Cloud service accounts (see [Cloud Setup](#cloud-setup))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/codebase-intelligence-mcp.git
cd codebase-intelligence-mcp

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your cloud service credentials
```

### Cloud Setup

1. **Qdrant Cloud**: Create cluster at [cloud.qdrant.io](https://cloud.qdrant.io) (Free tier: 1GB)
2. **Neo4j AuraDB**: Create instance at [neo4j.com/cloud/aura-free](https://neo4j.com/cloud/aura-free)
3. **Neon**: Create database at [neon.tech](https://neon.tech) (Free tier: 0.5GB)
4. **Upstash Redis**: Create database at [upstash.com](https://upstash.com) (Free tier: 10k commands/day)
5. **HuggingFace**: Get API token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Running Locally

```bash
# Start in stdio mode (for Cursor/Claude Desktop)
python -m src.server --mode stdio

# Start in HTTP mode (for testing)
python -m src.server --mode http --port 10000
```

### Using with Cursor/Claude Desktop

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "codebase-intelligence": {
      "command": "python",
      "args": ["-m", "src.server", "--mode", "stdio"],
      "cwd": "/path/to/codebase-intelligence-mcp",
      "env": {
        "QDRANT_URL": "your-qdrant-url",
        "QDRANT_API_KEY": "your-api-key",
        ...
      }
    }
  }
}
```

## MCP Tools

### 1. `index_codebase`
Index a directory for intelligent code analysis.

```json
{
  "path": "/path/to/codebase",
  "languages": ["python", "typescript"],
  "exclude_patterns": ["node_modules", "*.test.ts"]
}
```

### 2. `semantic_search`
Search code by meaning, not just text.

```json
{
  "query": "authentication middleware",
  "language_filter": "typescript",
  "top_k": 10
}
```

### 3. `analyze_dependencies`
Generate dependency graphs and detect circular dependencies.

```json
{
  "path": "/path/to/module",
  "language": "python",
  "depth": 3
}
```

### 4. `compute_metrics`
Calculate code complexity and quality metrics.

```json
{
  "file_path": "/path/to/file.py"
}
```

### 5. `detect_duplicates`
Find duplicate and similar code across the codebase.

```json
{
  "path": "/path/to/codebase",
  "similarity_threshold": 0.85
}
```

### 6. `generate_docs`
Auto-generate documentation from code.

```json
{
  "path": "/path/to/module",
  "format": "markdown"
}
```

### 7. `suggest_refactorings`
Get AI-powered refactoring suggestions.

```json
{
  "file_path": "/path/to/file.py"
}
```

### 8. `ask_codebase`
Query your codebase in natural language.

```json
{
  "question": "How does authentication work?",
  "top_k": 5
}
```

### 9. `get_call_graph`
Generate call graphs for functions.

```json
{
  "function_name": "authenticate_user",
  "max_depth": 2
}
```

### 10. `find_symbol`
Find symbol definitions and usages.

```json
{
  "symbol_name": "UserService",
  "symbol_type": "class"
}
```

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Connect Render to your repository
3. Add environment variables in Render dashboard
4. Deploy automatically on push to main

See [docs/deployment.md](docs/deployment.md) for detailed instructions.

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type check
mypy src/
```

## Performance

- Index 10k files in < 5 minutes
- Semantic search response < 500ms
- Dependency graph for 1k files < 2s
- Memory usage < 2GB for 100k files
- Supports 10+ concurrent clients

## Cost Estimation

**Development**: $0 (all services have generous free tiers)

**Production (100k files)**:
- Qdrant Cloud: $25/month
- Neo4j AuraDB: $65/month
- Neon PostgreSQL: $10/month
- Upstash Redis: $10/month
- HuggingFace API: ~$20/month
- Render: $7/month
- **Total: ~$137/month**

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read our contributing guidelines first.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/codebase-intelligence-mcp/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/codebase-intelligence-mcp/discussions)
