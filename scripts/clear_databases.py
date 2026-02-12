#!/usr/bin/env python3
"""Clear all data from Qdrant, Neon, and Neo4j databases."""

import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from neo4j import AsyncGraphDatabase
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

async def clear_qdrant():
    """Delete and recreate the Qdrant collection."""
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=60,
    )
    
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "codebase_vectors")
    
    try:
        # Delete existing collection
        client.delete_collection(collection_name=collection_name)
        print(f"✅ Deleted Qdrant collection: {collection_name}")
    except Exception as e:
        print(f"⚠️  Collection doesn't exist or error: {e}")
    
    # Recreate collection with new schema (includes 'project' field)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"✅ Created new Qdrant collection: {collection_name}")

def clear_neon():
    """Clear all tables in Neon PostgreSQL."""
    conn = psycopg2.connect(os.getenv("NEON_DATABASE_URL"))
    cursor = conn.cursor()
    
    try:
        # Drop and recreate tables
        cursor.execute("DROP TABLE IF EXISTS files CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS chunks CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS search_cache CASCADE;")
        conn.commit()
        print("✅ Cleared Neon PostgreSQL tables")
    except Exception as e:
        print(f"❌ Error clearing Neon: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

async def clear_neo4j():
    """Clear all nodes and relationships in Neo4j."""
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri or not password:
        print("⚠️  Neo4j not configured, skipping")
        return
    
    driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
    
    try:
        async with driver.session() as session:
            # Delete all nodes and relationships
            await session.run("MATCH (n) DETACH DELETE n")
            print("✅ Cleared Neo4j graph database (all nodes and relationships)")
    except Exception as e:
        print(f"❌ Error clearing Neo4j: {e}")
    finally:
        await driver.close()

async def main():
    print("🗑️  Clearing databases...")
    print()
    
    # Clear Qdrant
    await clear_qdrant()
    print()
    
    # Clear Neon
    clear_neon()
    print()
    
    # Clear Neo4j
    await clear_neo4j()
    print()
    
    print("✅ All databases cleared!")
    print("⚠️  Redis cache will auto-expire, no action needed")
    print()
    print("Next steps:")
    print("1. Restart your MCP server")
    print("2. Re-index your codebases with: index_codebase tool")

if __name__ == "__main__":
    asyncio.run(main())
