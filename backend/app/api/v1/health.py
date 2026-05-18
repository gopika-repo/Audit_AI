"""
Health check endpoints for API and external services.
"""

import time
from fastapi import APIRouter
from sqlalchemy import text

from app.core.logging import get_logger
from app.db.session import get_async_session_maker
from app.clients.redis_client import test_redis_connection
from app.clients.qdrant_client import test_qdrant_connection
from app.schemas.common import HealthCheckResponse

logger = get_logger()

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="API Health Check",
    description="Basic API health check endpoint",
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="ok",
        latency_ms=0.0,
        detail="API is running",
    )


@router.get(
    "/health/db",
    response_model=HealthCheckResponse,
    summary="Database Health Check",
    description="Check PostgreSQL database connectivity",
)
async def health_check_db() -> HealthCheckResponse:
    start_time = time.time()
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = (time.time() - start_time) * 1000
        return HealthCheckResponse(
            status="ok",
            latency_ms=round(latency_ms, 2),
            detail="Database connection successful",
        )
    except Exception as exc:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Database health check failed: {str(exc)}")
        return HealthCheckResponse(
            status="error",
            latency_ms=round(latency_ms, 2),
            detail=f"Database error: {str(exc)}",
        )


@router.get(
    "/health/redis",
    response_model=HealthCheckResponse,
    summary="Redis Health Check",
    description="Check Redis connection",
)
async def health_check_redis() -> HealthCheckResponse:
    start_time = time.time()
    try:
        is_healthy = await test_redis_connection()
        latency_ms = (time.time() - start_time) * 1000
        return HealthCheckResponse(
            status="ok" if is_healthy else "error",
            latency_ms=round(latency_ms, 2),
            detail="Redis connection successful" if is_healthy else "Redis connection failed",
        )
    except Exception as exc:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Redis health check failed: {str(exc)}")
        return HealthCheckResponse(
            status="error",
            latency_ms=round(latency_ms, 2),
            detail=f"Redis error: {str(exc)}",
        )


@router.get(
    "/health/qdrant",
    response_model=HealthCheckResponse,
    summary="Qdrant Health Check",
    description="Check Qdrant vector database connection",
)
async def health_check_qdrant() -> HealthCheckResponse:
    start_time = time.time()
    try:
        is_healthy = await test_qdrant_connection()
        latency_ms = (time.time() - start_time) * 1000
        return HealthCheckResponse(
            status="ok" if is_healthy else "error",
            latency_ms=round(latency_ms, 2),
            detail="Qdrant connection successful" if is_healthy else "Qdrant connection failed",
        )
    except Exception as exc:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Qdrant health check failed: {str(exc)}")
        return HealthCheckResponse(
            status="error",
            latency_ms=round(latency_ms, 2),
            detail=f"Qdrant error: {str(exc)}",
        )