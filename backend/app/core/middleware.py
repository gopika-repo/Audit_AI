"""
Middleware for request logging, error handling, and CORS.
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger()


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    settings = get_settings()

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging and timing middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable) -> None:
        """
        Middleware to log all HTTP requests with timing and request ID.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler function
            
        Returns:
            Response with request timing and ID
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.bind(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=round(process_time * 1000, 2),
            ).error(f"Unhandled exception: {str(exc)}", exc_info=exc)
            raise

        process_time = time.time() - start_time

        logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        ).info(f"{request.method} {request.url.path}")

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """
        Handle custom application exceptions.
        
        Args:
            request: FastAPI request object
            exc: Application exception
            
        Returns:
            JSON error response
        """
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.bind(request_id=request_id).error(
            f"Application error: {exc.message}",
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(request_id),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle general unhandled exceptions.
        
        Args:
            request: FastAPI request object
            exc: Unhandled exception
            
        Returns:
            JSON error response
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.bind(request_id=request_id).error(
            f"Unhandled exception: {str(exc)}",
            exc_info=exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc) if get_settings().DEBUG else "An error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "request_id": request_id,
            },
        )
