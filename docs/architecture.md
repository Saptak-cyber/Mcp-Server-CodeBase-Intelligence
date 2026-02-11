# Architecture Documentation

## System Overview

The Codebase Intelligence MCP Server is a cloud-native, production-grade system for code analysis and intelligence. It integrates 6 managed cloud services to provide scalable, high-performance code analysis capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client                            │
│              (Cursor / Claude Desktop)                   │
└────────────────────┬─────────────────────────────────────┘
                     │ MCP Protocol (stdio/HTTP)
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  MCP Server Core                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Parser  │  │  Search  │  │ Analysis │             │
│  │  Manager │  │  Engine  │  │  Engine  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        ↓             ↓             ↓
┌─────────────────────────────────────────────────────────┐
│                  Cloud Services                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Qdrant  │ │   Neo4j  │ │   Neon   │ │ Upstash  │ │
│  │  Vector  │ │  Graph   │ │PostgreSQL│ │  Redis   │ │
│  │   DB     │ │    DB    │ │          │ │  Cache   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                          │
│  ┌──────────────────────┐                               │
│  │   HuggingFace API    │                               │
│  │   (Embeddings)       │                               │
│  └──────────────────────┘                               │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. MCP Server Layer

**Responsibilities:**
- Handle MCP protocol communication (stdio/HTTP)
- Tool registry and invocation
- Request routing and validation
- Error handling and logging

**Key Components:**
- `server.py`: Main server implementation
- `tools/`: Tool implementations
- `config.py`: Configuration management

### 2. Parser Layer

**Responsibilities:**
- Multi-language code parsing using tree-sitter
- AST extraction and caching
- Symbol extraction (functions, classes, imports)

**Key Components:**
- `tree_sitter_manager.py`: Parser orchestrator
- `symbol_extractor.py`: Symbol extraction
- `ast_cache.py`: AST caching with Redis

### 3. Search Layer

**Responsibilities:**
- Code embedding generation
- Vector-based semantic search
- Code chunking for indexing

**Key Components:**
- `embeddings.py`: HuggingFace API integration
- `semantic_engine.py`: Search interface
- `chunker.py`: Code chunking logic
- `indexer.py`: Indexing coordinator

### 4. Analysis Layer

**Responsibilities:**
- Dependency graph analysis
- Code metrics calculation
- Call graph generation
- Refactoring suggestions

**Key Components:**
- `dependency_graph.py`: Neo4j graph analysis
- `calculator.py`: Metrics calculation
- `refactor/analyzer.py`: Refactoring analysis

### 5. Storage Layer

**Responsibilities:**
- Unified interface to cloud services
- Connection management
- Health monitoring

**Cloud Services:**
- **Qdrant Cloud**: Vector search for semantic queries
- **Neo4j AuraDB**: Graph database for dependencies
- **Neon PostgreSQL**: Metadata and metrics storage
- **Upstash Redis**: Distributed caching
- **HuggingFace**: Embedding generation

## Data Flow

### Indexing Flow

```
1. Scan directory for source files
2. For each file:
   a. Parse with tree-sitter → AST
   b. Extract symbols and chunks
   c. Generate embeddings (HuggingFace)
   d. Store vectors (Qdrant)
   e. Store metadata (Neon)
   f. Build dependency graph (Neo4j)
```

### Search Flow

```
1. Receive search query
2. Generate query embedding (HuggingFace)
3. Search vectors (Qdrant)
4. Filter and rank results
5. Cache results (Upstash Redis)
6. Return formatted response
```

### Analysis Flow

```
1. Retrieve file/directory
2. Parse code (tree-sitter)
3. Calculate metrics (radon)
4. Query dependencies (Neo4j)
5. Store results (Neon)
6. Return analysis report
```

## Scalability Design

### Caching Strategy

- **L1 Cache**: In-memory LRU cache for hot data
- **L2 Cache**: Upstash Redis for distributed caching
- **Cache Keys**: Structured as `module:operation:params`
- **TTL**: 30 minutes for search results, 2 hours for ASTs

### Batch Processing

- Embedding generation: Batches of 32
- File processing: Batches of 100
- Vector insertion: Bulk operations

### Async Operations

- All I/O operations are async
- Parallel file processing
- Background indexing tasks

## Security

### Authentication

- API key authentication for cloud services
- No storage of credentials in code
- Environment-based configuration

### Input Validation

- Path sanitization (prevent directory traversal)
- Language validation
- Rate limiting on expensive operations

### Data Protection

- TLS/SSL for all cloud connections
- No execution of arbitrary code
- Sandboxed file access

## Monitoring & Observability

### Metrics (Prometheus)

- Tool invocation counters
- Execution duration histograms
- Error rates
- Cache hit/miss rates

### Logging (structlog)

- Structured JSON logs
- Correlation IDs for requests
- Error tracking with context
- Performance metrics

### Health Checks

- Individual service health endpoints
- Overall system health status
- Automatic health monitoring

## Deployment

### Local Development

```bash
python -m src.server --mode stdio
```

### Production (Render)

- Automatic deployment from GitHub
- Environment variable configuration
- Auto-scaling based on traffic
- Built-in monitoring

## Performance Targets

- **Indexing**: 10k files in < 5 minutes
- **Search**: Response < 500ms
- **Dependencies**: 1k files in < 2s
- **Memory**: < 2GB for 100k files
- **Concurrency**: 10+ simultaneous clients
