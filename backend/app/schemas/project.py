"""Pydantic schemas for project APIs."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.pagination import PaginatedResponse


class ProjectBase(BaseModel):
    """Base schema with shared project fields."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str = Field(..., min_length=1, description="Project description")
    domain: str = Field(..., min_length=1, max_length=100, description="Project domain")
    ai_category: Optional[str] = Field(None, max_length=100, description="AI category")
    tech_stack: dict[str, Any] = Field(default_factory=dict, description="Technology stack")
    repo_url: Optional[str] = Field(None, max_length=500, description="Repository URL")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    domain: Optional[str] = Field(None, min_length=1, max_length=100)
    ai_category: Optional[str] = Field(None, max_length=100)
    tech_stack: Optional[dict[str, Any]] = None
    repo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Schema for project API responses."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: UUID = Field(..., description="Project identifier")
    is_active: bool = Field(..., description="Whether the project is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProjectFilter(BaseModel):
    """Query params used to filter project lists."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    name: Optional[str] = Field(None, description="Filter by exact project name")
    domain: Optional[str] = Field(None, description="Filter by domain")
    ai_category: Optional[str] = Field(None, description="Filter by AI category")
    is_active: Optional[bool] = Field(None, description="Filter by active state")
    search: Optional[str] = Field(None, description="Search by name or description")


class ProjectListResponse(PaginatedResponse[ProjectResponse]):
    """Paginated list response for projects."""


ProjectList = ProjectListResponse
