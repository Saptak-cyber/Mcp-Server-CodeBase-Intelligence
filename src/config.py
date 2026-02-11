"""Configuration management for the MCP server."""

import os
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server Configuration
    mcp_server_mode: str = Field(default="stdio", description="Server mode: stdio or http")
    port: int = Field(default=10000, description="HTTP server port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Qdrant Cloud
    qdrant_url: str = Field(default="", description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(default="", description="Qdrant API key")
    qdrant_collection_name: str = Field(
        default="codebase_intelligence", description="Qdrant collection name"
    )

    # HuggingFace
    huggingface_api_key: str = Field(default="", description="HuggingFace API key")
    huggingface_model: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="HuggingFace embedding model",
    )

    # Neo4j Cloud
    neo4j_uri: str = Field(default="", description="Neo4j connection URI")
    neo4j_username: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="", description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")

    # Neon PostgreSQL
    neon_database_url: str = Field(default="", description="Neon PostgreSQL connection URL")

    # Upstash Redis
    upstash_redis_url: str = Field(default="", description="Upstash Redis URL")
    upstash_redis_token: str = Field(default="", description="Upstash Redis token")

    # Feature Flags
    enable_caching: bool = Field(default=True, description="Enable Redis caching")
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")

    # Processing Configuration
    batch_size: int = Field(default=32, description="Batch size for processing")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
