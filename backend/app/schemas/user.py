"""
Pydantic schemas for User model.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRole = Field(default=UserRole.FRESHER, description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserList(BaseModel):
    """Schema for list of users."""

    model_config = ConfigDict(from_attributes=True)

    total: int = Field(..., description="Total count")
    items: list[UserResponse] = Field(default_factory=list, description="Users list")
