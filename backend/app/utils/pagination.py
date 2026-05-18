"""Pagination utilities for API responses."""

from __future__ import annotations

from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    page: int = Field(default=1, ge=1, description="1-based page number")
    page_size: int = Field(default=10, ge=1, le=1000, description="Number of items per page")

    @property
    def offset(self) -> int:
        """Return the row offset for the current page."""

        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    model_config = ConfigDict(from_attributes=True)

    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0


async def paginate_query(
    session: AsyncSession,
    query: Select[Any],
    params: PaginationParams,
) -> tuple[list[Any], int]:
    """Execute a paginated select statement and return items plus total count."""

    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total_count = await session.scalar(count_query)
    total = int(total_count or 0)

    paginated_query = query.offset(params.offset).limit(params.page_size)
    result = await session.execute(paginated_query)
    items = list(result.scalars().all())
    return items, total


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the number of pages required for the given total."""

    if total <= 0 or page_size <= 0:
        return 0
    return ceil(total / page_size)


def get_offset_from_page(page: int, page_size: int) -> int:
    """Convert a page number into an offset."""

    page = max(page, 1)
    page_size = max(page_size, 1)
    return (page - 1) * page_size
