# Deployment Guide

## Prerequisites

- Python 3.11+
- Cloud service accounts:
  - Qdrant Cloud
  - Neo4j AuraDB
  - Neon PostgreSQL
  - Upstash Redis
  - HuggingFace (API token)
- GitHub account (for Render deployment)

## Local Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/codebase-intelligence-mcp.git
cd codebase-intelligence-mcp

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run Locally

**Stdio mode (for Cursor/Claude Desktop):**
```bash
python -m src.server --mode stdio
```

**HTTP mode (for testing):**
```bash
python -m src.server --mode http --port 10000
```

## Cloud Service Setup

### Qdrant Cloud

1. Visit [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free cluster
3. Note the cluster URL and API key
4. Add to `.env`:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_key
   ```

### Neo4j AuraDB

1. Visit [neo4j.com/cloud/aura-free](https://neo4j.com/cloud/aura-free)
2. Create a free instance
3. Note the connection URI, username, and password
4. Add to `.env`:
   ```
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

### Neon PostgreSQL

1. Visit [neon.tech](https://neon.tech)
2. Create a project
3. Copy the connection string
4. Add to `.env`:
   ```
   NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname
   ```

### Upstash Redis

1. Visit [upstash.com](https://upstash.com)
2. Create a Redis database
3. Copy the REST URL and token
4. Add to `.env`:
   ```
   UPSTASH_REDIS_URL=https://xxx.upstash.io
   UPSTASH_REDIS_TOKEN=your_token
   ```

### HuggingFace

1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token
3. Add to `.env`:
   ```
   HUGGINGFACE_API_KEY=hf_xxxxx
   ```

## Cursor/Claude Desktop Integration

Add to your MCP configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "codebase-intelligence": {
      "command": "python",
      "args": ["-m", "src.server", "--mode", "stdio"],
      "cwd": "/absolute/path/to/codebase-intelligence-mcp",
      "env": {
        "QDRANT_URL": "https://your-cluster.qdrant.io",
        "QDRANT_API_KEY": "your_key",
        "HUGGINGFACE_API_KEY": "hf_xxxxx",
        "NEO4J_URI": "neo4j+s://xxx.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your_password",
        "NEON_DATABASE_URL": "postgresql://...",
        "UPSTASH_REDIS_URL": "https://xxx.upstash.io",
        "UPSTASH_REDIS_TOKEN": "your_token"
      }
    }
  }
}
```

Restart Cursor/Claude Desktop to load the configuration.

## Production Deployment on Render

### 1. Prepare Repository

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Connect to Render

1. Visit [render.com](https://render.com)
2. Sign up / Sign in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository

### 3. Configure Service

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -m src.server --mode http --port 10000
```

**Environment Variables:**
Add all variables from `.env` in Render dashboard

### 4. Deploy

- Render will automatically deploy
- Get your deployment URL: `https://your-app.onrender.com`

### 5. Configure MCP Client for Production

```json
{
  "mcpServers": {
    "codebase-intelligence": {
      "url": "https://your-app.onrender.com/sse",
      "transport": "sse"
    }
  }
}
```

## Docker Deployment

### Build Image

```bash
docker build -t codebase-intelligence-mcp .
```

### Run Container

```bash
docker run -p 10000:10000 --env-file .env codebase-intelligence-mcp
```

### Docker Compose

```bash
docker-compose up
```

## Health Monitoring

### Health Check Endpoint

```bash
curl http://localhost:10000/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "qdrant": true,
    "neo4j": true,
    "neon": true,
    "upstash": true
  }
}
```

### Prometheus Metrics

Available at: `http://localhost:9090/metrics`

Key metrics:
- `mcp_tool_calls_total`
- `mcp_tool_duration_seconds`

## Troubleshooting

### Connection Errors

**Symptom:** Can't connect to cloud services

**Solution:**
1. Verify credentials in `.env`
2. Check network connectivity
3. Verify cloud service status
4. Check firewall rules

### Performance Issues

**Symptom:** Slow indexing or search

**Solution:**
1. Increase batch sizes in config
2. Enable caching
3. Check cloud service quotas
4. Monitor Prometheus metrics

### Import Errors

**Symptom:** Module import failures

**Solution:**
1. Reinstall dependencies: `pip install -r requirements.txt`
2. Check Python version (3.11+)
3. Verify virtual environment is activated

## Scaling

### Horizontal Scaling

- Use Render's auto-scaling features
- Configure min/max instances
- Set up load balancing

### Vertical Scaling

- Upgrade Render plan for more resources
- Increase cloud service tiers
- Optimize batch sizes and caching

## Security Best Practices

1. **Never commit `.env` files**
2. **Rotate API keys regularly**
3. **Use Render's secret management**
4. **Enable rate limiting**
5. **Monitor access logs**
6. **Keep dependencies updated**

## Monitoring & Logging

### Render Dashboard

- View real-time logs
- Monitor CPU/memory usage
- Track deployment history
- Set up alerts

### Structured Logging

All logs are in JSON format with:
- Timestamp
- Log level
- Message
- Context data
- Correlation IDs

## Backup & Recovery

### Database Backups

- Neon: Automatic backups
- Neo4j: Export with `neo4j-admin dump`
- Qdrant: Snapshots via API

### Disaster Recovery

1. Document all cloud configurations
2. Store credentials securely
3. Regular backup testing
4. Maintain deployment runbooks
