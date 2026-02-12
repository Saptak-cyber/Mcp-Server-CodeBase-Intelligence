"""Neo4j Cloud graph database integration."""

from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class Neo4jStore:
    """Neo4j Cloud graph database manager."""

    def __init__(self) -> None:
        """Initialize Neo4j driver."""
        settings = get_settings()
        self.driver: Optional[AsyncDriver] = None
        self.uri = settings.neo4j_uri
        self.username = settings.neo4j_username
        self.password = settings.neo4j_password
        self.database = settings.neo4j_database
        self._enabled = bool(self.uri and self.password)

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        if not self._enabled:
            logger.warning("Neo4j not configured, skipping connection")
            return

        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.username, self.password))
            await self.driver.verify_connectivity()
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))
            self._enabled = False

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query."""
        if not self._enabled:
            logger.warning("Neo4j not available")
            return []

        if not self.driver:
            await self.connect()

        assert self.driver is not None  # Should be set by connect()
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run(query, parameters or {})
                records = [record.data() async for record in result]
                return records
        except Exception as e:
            logger.error("Query execution failed", query=query, error=str(e))
            raise

    async def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a node in the graph."""
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"

        results = await self.execute_query(query, properties)
        return results[0]["n"] if results else {}

    async def create_relationship(
        self,
        from_label: str,
        from_property: str,
        from_value: Any,
        to_label: str,
        to_property: str,
        to_value: Any,
        rel_type: str,
        rel_properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a relationship between nodes."""
        rel_props = ""
        if rel_properties:
            props_str = ", ".join([f"{k}: ${k}" for k in rel_properties.keys()])
            rel_props = f" {{{props_str}}}"

        query = f"""
        MATCH (a:{from_label} {{{from_property}: $from_value}})
        MATCH (b:{to_label} {{{to_property}: $to_value}})
        MERGE (a)-[r:{rel_type}{rel_props}]->(b)
        RETURN r
        """

        params = {
            "from_value": from_value,
            "to_value": to_value,
            **(rel_properties or {}),
        }

        await self.execute_query(query, params)

    async def find_circular_dependencies(self) -> List[Dict[str, Any]]:
        """Find circular dependencies in the graph."""
        query = """
        MATCH (m1:Module)-[:DEPENDS_ON*]->(m2:Module)-[:DEPENDS_ON*]->(m1)
        WHERE id(m1) < id(m2)
        RETURN DISTINCT m1.name as module1, m2.name as module2
        LIMIT 100
        """
        return await self.execute_query(query)

    async def get_dependencies(self, node_name: str, depth: int = 3) -> List[Dict[str, Any]]:
        """Get dependencies for a node up to specified depth."""
        query = f"""
        MATCH path = (n:Module {{name: $name}})-[:DEPENDS_ON*1..{depth}]->(dep)
        RETURN path
        LIMIT 100
        """
        return await self.execute_query(query, {"name": node_name})

    async def get_most_called_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most called functions."""
        query = """
        MATCH (f:Function)<-[c:CALLS]-()
        RETURN f.name as function, count(c) as call_count
        ORDER BY call_count DESC
        LIMIT $limit
        """
        return await self.execute_query(query, {"limit": limit})

    async def calculate_module_coupling(self) -> List[Dict[str, Any]]:
        """Calculate coupling score for modules."""
        query = """
        MATCH (m:Module)-[d:DEPENDS_ON]->(other:Module)
        RETURN m.name as module, count(d) as coupling_score
        ORDER BY coupling_score DESC
        """
        return await self.execute_query(query)

    async def clear_graph(self) -> None:
        """Clear all nodes and relationships (use with caution)."""
        query = "MATCH (n) DETACH DELETE n"
        await self.execute_query(query)
        logger.warning("Graph cleared")

    async def health_check(self) -> bool:
        """Check Neo4j connection health."""
        if not self._enabled:
            return False

        try:
            if not self.driver:
                await self.connect()
            if self.driver:
                await self.driver.verify_connectivity()
                return True
            return False
        except Exception as e:
            logger.error("Neo4j health check failed", error=str(e))
            return False
