"""
Pydantic schemas for common response models.
"""

from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseResponse(BaseModel):
    """Base response model with common fields."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class PaginatedResponse(BaseResponse):
    """
    Generic paginated response wrapper.
    
    Attributes:
        data: List of items
        total: Total count of items
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages
    """

    data: list = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0


class HealthCheckResponse(BaseResponse):
    """
    Health check response model.
    
    Attributes:
        status: Health status (ok, error)
        latency_ms: Response latency in milliseconds
        detail: Additional detail message
    """

    status: str = Field(..., description="Health status")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    detail: str = Field(..., description="Detail message")


class ErrorResponse(BaseResponse):
    """
    Error response model.
    
    Attributes:
        error: Error message
        detail: Detailed error information
        status_code: HTTP status code
        request_id: Request tracking ID
    """

    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
    request_id: str = Field(..., description="Request tracking ID")
