"""
FastAPI application factory and main entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import setup_middleware
from app.db.session import init_db_engine, close_db_engine
from app.clients.redis_client import init_redis, close_redis
from app.clients.qdrant_client import init_qdrant, close_qdrant
from app.services.embedding_service import init_embedding_service
from app.services.vector_store_service import init_vector_store_service
from app.api import router

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup events
    try:
        logger.info("Starting up application...")
        
        # Initialize database
        await init_db_engine()
        
        # Initialize Redis
        await init_redis()
        
        # Initialize Qdrant
        await init_qdrant()
        
        # Initialize embedding service
        init_embedding_service()
        
        # Initialize vector store service
        await init_vector_store_service()
        
        logger.info("Application startup complete")
        
    except Exception as exc:
        logger.error(f"Application startup failed: {str(exc)}", exc_info=exc)
        raise

    yield

    # Shutdown events
    try:
        logger.info("Shutting down application...")
        
        # Close all connections
        await close_qdrant()
        await close_redis()
        await close_db_engine()
        
        logger.info("Application shutdown complete")
        
    except Exception as exc:
        logger.error(f"Application shutdown error: {str(exc)}", exc_info=exc)


def create_app() -> FastAPI:
    """
    FastAPI application factory.
    Creates and configures the FastAPI application with all middleware,
    routers, and exception handlers.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()

    # Setup logging
    setup_logging(
        debug=settings.DEBUG,
        environment=settings.ENVIRONMENT,
    )

    logger.info(
        f"Creating FastAPI application: {settings.APP_NAME} "
        f"(env={settings.ENVIRONMENT}, debug={settings.DEBUG})"
    )

    # Create FastAPI app with lifespan
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered Engineering Onboarding & Knowledge Operating System",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # Setup middleware
    setup_middleware(app)

    # Include API routers
    app.include_router(router)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint - API is running."""
        return {
            "message": "Welcome to AI Engineering Onboarding System",
            "version": "0.1.0",
            "docs": "/docs" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        }

    logger.info("FastAPI application created successfully")
    return app


# Create app instance for uvicorn
app = create_app()
