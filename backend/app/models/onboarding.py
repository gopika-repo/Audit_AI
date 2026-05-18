"""
OnboardingProgress model tracking user progress through projects.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class OnboardingStatus(str, PyEnum):
    """Enumeration of onboarding progress statuses."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OnboardingProgress(BaseModel):
    """
    OnboardingProgress model tracking a user's progress through a project.
    
    Attributes:
        user_id: Foreign key to User model
        project_id: Foreign key to Project model
        status: Current progress status (not_started, in_progress, completed)
        progress_percentage: Percentage of project completed (0-100)
        started_at: Timestamp when onboarding started
        completed_at: Timestamp when onboarding was completed
    """

    __tablename__ = "onboarding_progress"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus, native_enum=False),
        default=OnboardingStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<OnboardingProgress(id={self.id}, user_id={self.user_id}, "
            f"project_id={self.project_id}, status={self.status})>"
        )
