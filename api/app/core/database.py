"""
Database configuration and session management
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, text
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG
)

# Create sync session factory
sync_session = sessionmaker(bind=sync_engine)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to register them
            from app.models import (
                user, organization, media, job, 
                transcript, export, webhook, usage, audit
            )
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


async def get_db_health() -> bool:
    """Check database health"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


async def drop_tables():
    """Drop all database tables (for testing/development)"""
    try:
        async with engine.begin() as conn:
            from app.models import (
                user, organization, media, job,
                transcript, export, webhook, usage, audit
            )
            
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error("Failed to drop database tables", error=str(e))
        raise


def get_sync_db():
    """Get synchronous database session (for migrations, etc.)"""
    db = sync_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Database utilities
class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    async def execute_raw_sql(query: str, params: Optional[dict] = None):
        """Execute raw SQL query"""
        async with async_session() as session:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
    
    @staticmethod
    async def check_table_exists(table_name: str) -> bool:
        """Check if table exists"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = :table_name
        );
        """
        result = await DatabaseUtils.execute_raw_sql(query, {"table_name": table_name})
        return result.scalar()
    
    @staticmethod
    async def get_table_count(table_name: str) -> int:
        """Get row count for table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = await DatabaseUtils.execute_raw_sql(query)
        return result.scalar()
    
    @staticmethod
    async def optimize_table(table_name: str):
        """Optimize table (PostgreSQL VACUUM ANALYZE)"""
        query = f"VACUUM ANALYZE {table_name}"
        await DatabaseUtils.execute_raw_sql(query)
    
    @staticmethod
    async def create_index_if_not_exists(index_name: str, table_name: str, columns: str):
        """Create index if it doesn't exist"""
        query = f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
        ON {table_name} ({columns})
        """
        await DatabaseUtils.execute_raw_sql(query)


# Database monitoring
class DatabaseMonitor:
    """Database monitoring utilities"""
    
    @staticmethod
    async def get_connection_stats():
        """Get database connection statistics"""
        query = """
        SELECT 
            count(*) as total_connections,
            count(*) FILTER (WHERE state = 'active') as active_connections,
            count(*) FILTER (WHERE state = 'idle') as idle_connections
        FROM pg_stat_activity 
        WHERE datname = current_database()
        """
        result = await DatabaseUtils.execute_raw_sql(query)
        return result.fetchone()._asdict()
    
    @staticmethod
    async def get_database_size():
        """Get database size in MB"""
        query = """
        SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """
        result = await DatabaseUtils.execute_raw_sql(query)
        return result.scalar()
    
    @staticmethod
    async def get_table_sizes():
        """Get table sizes"""
        query = """
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """
        result = await DatabaseUtils.execute_raw_sql(query)
        return [dict(row) for row in result.fetchall()]
    
    @staticmethod
    async def get_slow_queries():
        """Get slow running queries"""
        query = """
        SELECT 
            pid,
            now() - pg_stat_activity.query_start AS duration,
            query,
            state
        FROM pg_stat_activity 
        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
        ORDER BY duration DESC
        """
        result = await DatabaseUtils.execute_raw_sql(query)
        return [dict(row) for row in result.fetchall()]


# Export database utilities
db_utils = DatabaseUtils()
db_monitor = DatabaseMonitor()