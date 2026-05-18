"""
SQLAlchemy async session factory and engine configuration.
Provides dependency injection for database sessions in FastAPI routes.
"""

from typing import AsyncGenerator

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()

# Global async engine and session factory
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


async def init_db_engine() -> None:
    """
    Initialize the async SQLAlchemy engine and session factory.
    Should be called on application startup.
    """
    global _engine, _async_session_maker

    settings = get_settings()

    try:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.SQLALCHEMY_ECHO,
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=0,
        )

        _async_session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        logger.info(f"Database engine initialized: {settings.DATABASE_URL}")
    except Exception as exc:
        logger.exception("Failed to initialize database engine")
        raise


async def close_db_engine() -> None:
    """
    Close the async SQLAlchemy engine.
    Should be called on application shutdown.
    """
    global _engine

    if _engine:
        try:
            await _engine.dispose()
            logger.info("Database engine disposed")
        except Exception as exc:
            logger.exception("Error disposing database engine")


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get the async session maker factory.
    
    Returns:
        AsyncSession factory
        
    Raises:
        RuntimeError: If engine is not initialized
    """
    if _async_session_maker is None:
        raise RuntimeError("Database engine not initialized. Call init_db_engine() first.")
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for AsyncSession in FastAPI routes.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception as exc:
            logger.exception("Database session error")
            await session.rollback()
            raise
        finally:
            await session.close()
