"""
SQLAlchemy declarative base and base model for all ORM models.
Provides common fields and functionality for all database models.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class BaseModel(Base):
    """
    Abstract base model with common fields for all entities.
    Provides id, created_at, and updated_at fields.
    """

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
