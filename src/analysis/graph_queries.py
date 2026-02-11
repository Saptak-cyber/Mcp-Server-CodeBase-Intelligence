"""Graph query utilities for Neo4j."""

from typing import List, Dict, Any
from ..storage.neo4j_store import Neo4jStore
from ..utils.logging import get_logger

logger = get_logger(__name__)


class GraphQueryExecutor:
    """Execute common graph queries."""

    def __init__(self, neo4j: Neo4jStore):
        """Initialize query executor."""
        self.neo4j = neo4j

    async def find_shortest_path(
        self, from_node: str, to_node: str
    ) -> List[Dict[str, Any]]:
        """Find shortest path between nodes."""
        query = """
        MATCH path = shortestPath(
            (from:Module {name: $from})-[*]-(to:Module {name: $to})
        )
        RETURN path
        """
        return await self.neo4j.execute_query(query, {"from": from_node, "to": to_node})

    async def get_node_neighbors(
        self, node_name: str, relationship: str = "DEPENDS_ON"
    ) -> List[Dict[str, Any]]:
        """Get neighbors of a node."""
        query = f"""
        MATCH (n:Module {{name: $name}})-[:{relationship}]->(neighbor)
        RETURN neighbor.name as name
        """
        return await self.neo4j.execute_query(query, {"name": node_name})

    async def calculate_centrality(self) -> List[Dict[str, Any]]:
        """Calculate node centrality scores."""
        query = """
        MATCH (n:Module)
        RETURN n.name as module,
               size((n)-[:DEPENDS_ON]->()) as out_degree,
               size((n)<-[:DEPENDS_ON]-()) as in_degree
        ORDER BY in_degree DESC
        LIMIT 20
        """
        return await self.neo4j.execute_query(query)
