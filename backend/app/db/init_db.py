"""
Database initialization and utilities.
Handles database setup, table creation, and connection validation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import get_async_session_maker

logger = get_logger()


async def create_all_tables() -> None:
    """
    Create all database tables based on SQLAlchemy models.
    Typically called on startup or during migration setup.
    """
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            async with session.begin():
                # Import all models to register them with Base
                from app import models  # noqa: F401

                # Create all tables
                await session.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
    except Exception as exc:
        logger.error(f"Failed to create database tables: {str(exc)}", exc_info=exc)
        raise


async def drop_all_tables() -> None:
    """
    Drop all database tables.
    WARNING: This will delete all data. Use only in development/testing.
    """
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            async with session.begin():
                await session.run_sync(Base.metadata.drop_all)
                logger.warning("All database tables dropped")
    except Exception as exc:
        logger.error(f"Failed to drop database tables: {str(exc)}", exc_info=exc)
        raise


async def test_database_connection() -> bool:
    """
    Test database connectivity.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            await session.execute("SELECT 1")
            logger.debug("Database connection test successful")
            return True
    except Exception as exc:
        logger.error(f"Database connection test failed: {str(exc)}", exc_info=exc)
        return False
