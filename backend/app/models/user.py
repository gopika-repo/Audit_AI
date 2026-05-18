"""
User model representing system users (engineers, admins, etc).
"""

from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class UserRole(str, PyEnum):
    """Enumeration of user roles."""

    ADMIN = "admin"
    ENGINEER = "engineer"
    FRESHER = "fresher"


class User(BaseModel):
    """
    User model for storing user information.
    
    Attributes:
        email: User email address (unique)
        full_name: User's full name
        role: User's role (admin, engineer, fresher)
        is_active: Whether the user account is active
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.FRESHER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
