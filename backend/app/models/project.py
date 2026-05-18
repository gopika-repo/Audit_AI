"""
Project model representing onboarding projects and domains.
"""

from typing import Optional

from sqlalchemy import String, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Project(BaseModel):
    """
    Project model for storing engineering projects and onboarding topics.
    
    Attributes:
        name: Project name
        description: Detailed project description
        domain: Domain or category (e.g., 'backend', 'frontend', 'infra')
        ai_category: AI/ML category if applicable
        tech_stack: JSON field containing list of technologies
        repo_url: Optional URL to the project repository
        is_active: Whether the project is available for onboarding
    """

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ai_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tech_stack: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, domain={self.domain})>"
