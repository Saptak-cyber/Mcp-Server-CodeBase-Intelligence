"""Neon PostgreSQL storage for metadata and metrics."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Index,
    select,
    delete,
)
from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)

Base = declarative_base()


class File(Base):
    """File metadata table."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    path = Column(String(1000), unique=True, nullable=False, index=True)
    language = Column(String(50), nullable=False, index=True)
    size_bytes = Column(Integer)
    last_modified = Column(DateTime, nullable=False)
    last_indexed = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_language_path", "language", "path"),)


class Metric(Base):
    """Code metrics table."""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    file_path = Column(String(1000), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # file, class, function
    entity_name = Column(String(500), nullable=False)
    cyclomatic_complexity = Column(Float)
    cognitive_complexity = Column(Float)
    maintainability_index = Column(Float)
    sloc = Column(Integer)
    comment_lines = Column(Integer)
    blank_lines = Column(Integer)
    computed_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_file_entity", "file_path", "entity_type", "entity_name"),
        Index("idx_complexity", "cyclomatic_complexity"),
    )


class ComplexityHotspot(Base):
    """Cache for high complexity locations."""

    __tablename__ = "complexity_hotspots"

    id = Column(Integer, primary_key=True)
    file_path = Column(String(1000), nullable=False, index=True)
    entity_name = Column(String(500), nullable=False)
    complexity_score = Column(Float, nullable=False, index=True)
    issue_type = Column(String(100))
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NeonStore:
    """Neon PostgreSQL storage manager."""

    def __init__(self):
        """Initialize Neon connection."""
        settings = get_settings()
        self.db_url = settings.neon_database_url
        self._enabled = bool(self.db_url)
        self.engine = None
        self.async_session = None
        
        if self._enabled:
            # Convert postgresql:// to postgresql+asyncpg://
            db_url = self.db_url.replace("postgresql://", "postgresql+asyncpg://")
            
            # Convert psycopg2 SSL parameters to asyncpg format
            # asyncpg doesn't support 'sslmode' but uses 'ssl' instead
            db_url = db_url.replace("sslmode=require", "ssl=require")
            db_url = db_url.replace("sslmode=prefer", "ssl=prefer")
            db_url = db_url.replace("sslmode=allow", "ssl=true")
            db_url = db_url.replace("sslmode=disable", "ssl=false")
            
            # Remove channel_binding parameter (not supported by asyncpg)
            if "channel_binding=" in db_url:
                import re
                db_url = re.sub(r'[&?]channel_binding=[^&]*', '', db_url)
            
            self.engine = create_async_engine(db_url, echo=False, pool_size=5, max_overflow=10)
            self.async_session = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        if not self._enabled or not self.engine:
            logger.warning("Neon not configured, skipping initialization")
            return
            
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Neon database tables initialized")
        except Exception as e:
            logger.error("Failed to initialize Neon database", error=str(e))
            self._enabled = False

    async def upsert_file(self, file_data: Dict[str, Any]) -> None:
        """Insert or update file metadata."""
        if not self._enabled or not self.async_session:
            return
            
        async with self.async_session() as session:
            try:
                # Check if file exists
                result = await session.execute(
                    select(File).where(File.path == file_data["path"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    for key, value in file_data.items():
                        setattr(existing, key, value)
                else:
                    new_file = File(**file_data)
                    session.add(new_file)

                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Failed to upsert file", error=str(e))
                raise

    async def insert_metrics(self, metrics_data: List[Dict[str, Any]]) -> None:
        """Insert code metrics."""
        if not self._enabled or not self.async_session:
            return
            
        async with self.async_session() as session:
            try:
                metrics = [Metric(**data) for data in metrics_data]
                session.add_all(metrics)
                await session.commit()
                logger.info(f"Inserted {len(metrics)} metrics")
            except Exception as e:
                await session.rollback()
                logger.error("Failed to insert metrics", error=str(e))
                raise

    async def get_file_metrics(self, file_path: str) -> List[Dict[str, Any]]:
        """Get metrics for a file."""
        if not self._enabled or not self.async_session:
            return []
            
        async with self.async_session() as session:
            result = await session.execute(
                select(Metric).where(Metric.file_path == file_path)
            )
            metrics = result.scalars().all()
            return [
                {
                    "entity_type": m.entity_type,
                    "entity_name": m.entity_name,
                    "cyclomatic_complexity": m.cyclomatic_complexity,
                    "cognitive_complexity": m.cognitive_complexity,
                    "maintainability_index": m.maintainability_index,
                    "sloc": m.sloc,
                    "comment_lines": m.comment_lines,
                    "blank_lines": m.blank_lines,
                }
                for m in metrics
            ]

    async def get_complexity_hotspots(
        self, min_complexity: float = 10.0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get high complexity code locations."""
        async with self.async_session() as session:
            result = await session.execute(
                select(ComplexityHotspot)
                .where(ComplexityHotspot.complexity_score >= min_complexity)
                .order_by(ComplexityHotspot.complexity_score.desc())
                .limit(limit)
            )
            hotspots = result.scalars().all()
            return [
                {
                    "file_path": h.file_path,
                    "entity_name": h.entity_name,
                    "complexity_score": h.complexity_score,
                    "issue_type": h.issue_type,
                    "description": h.description,
                }
                for h in hotspots
            ]

    async def update_hotspots(self, hotspots_data: List[Dict[str, Any]]) -> None:
        """Update complexity hotspots."""
        async with self.async_session() as session:
            try:
                # Clear old hotspots
                await session.execute(delete(ComplexityHotspot))

                # Insert new hotspots
                hotspots = [ComplexityHotspot(**data) for data in hotspots_data]
                session.add_all(hotspots)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Failed to update hotspots", error=str(e))
                raise

    async def get_indexed_files(
        self, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of indexed files."""
        async with self.async_session() as session:
            query = select(File)
            if language:
                query = query.where(File.language == language)

            result = await session.execute(query)
            files = result.scalars().all()
            return [{"path": f.path, "language": f.language} for f in files]

    async def close(self) -> None:
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Neon connection closed")

    async def health_check(self) -> bool:
        """Check Neon connection health."""
        if not self._enabled or not self.async_session:
            return False
            
        try:
            async with self.async_session() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            logger.error("Neon health check failed", error=str(e))
            return False
