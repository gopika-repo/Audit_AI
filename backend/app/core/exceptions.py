"""
Custom exception classes for the application.
Provides consistent error handling and response formatting.
"""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
    ):
        """
        Initialize AppException.
        
        Args:
            message: Main error message
            status_code: HTTP status code
            detail: Detailed error information
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)

    def to_dict(self, request_id: str) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.
        
        Args:
            request_id: Request ID for tracing
            
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": self.message,
            "detail": self.detail,
            "status_code": self.status_code,
            "request_id": request_id,
        }


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, detail: Optional[str] = None):
        """
        Initialize NotFoundError.
        
        Args:
            resource: Name of the resource that was not found
            detail: Additional detail about what was not found
        """
        message = f"{resource} not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or message,
        )


class ValidationError(AppException):
    """Validation error exception."""

    def __init__(self, message: str, detail: Optional[str] = None):
        """
        Initialize ValidationError.
        
        Args:
            message: Validation error message
            detail: Additional validation details
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail or message,
        )


class UnauthorizedError(AppException):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized", detail: Optional[str] = None):
        """
        Initialize UnauthorizedError.
        
        Args:
            message: Unauthorized message
            detail: Additional authorization details
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or message,
        )


class DatabaseError(AppException):
    """Database operation error exception."""

    def __init__(self, message: str, detail: Optional[str] = None):
        """
        Initialize DatabaseError.
        
        Args:
            message: Database error message
            detail: Additional database error details
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or message,
        )


class ExternalServiceError(AppException):
    """External service communication error exception."""

    def __init__(self, service: str, detail: Optional[str] = None):
        """
        Initialize ExternalServiceError.
        
        Args:
            service: Name of the external service
            detail: Error details from the service
        """
        message = f"{service} service error"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail or message,
        )
