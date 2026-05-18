"""Async business logic for project operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectFilter, ProjectUpdate
from app.utils.pagination import PaginationParams, paginate_query


class ProjectService:
    """Service layer for project persistence and query logic."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the service with an async database session."""

        self.db = db

    async def _get_project_by_name(self, name: str) -> Project | None:
        """Return an active project matching the provided name."""

        result = await self.db.execute(
            select(Project).where(
                func.lower(Project.name) == name.lower(),
                Project.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    def _build_query(self, filters: ProjectFilter | None = None) -> Select[Any]:
        """Build the base project select statement for list operations."""

        query = select(Project)
        filters = filters or ProjectFilter()

        conditions = []
        if filters.is_active is None:
            conditions.append(Project.is_active.is_(True))
        else:
            conditions.append(Project.is_active.is_(filters.is_active))
        if filters.name:
            conditions.append(Project.name == filters.name)
        if filters.domain:
            conditions.append(Project.domain == filters.domain)
        if filters.ai_category:
            conditions.append(Project.ai_category == filters.ai_category)
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            conditions.append(
                or_(
                    func.lower(Project.name).ilike(search_term),
                    func.lower(Project.description).ilike(search_term),
                )
            )

        return query.where(and_(*conditions)).order_by(Project.created_at.desc())

    async def get_all_projects(
        self,
        filters: ProjectFilter | None,
        pagination: PaginationParams,
    ) -> tuple[list[Project], int]:
        """Return a paginated list of projects and the total matching count."""

        query = self._build_query(filters)
        items, total = await paginate_query(self.db, query, pagination)
        return items, total

    async def get_project_by_id(self, project_id: UUID) -> Project | None:
        """Return an active project by its UUID."""

        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create_project(self, data: ProjectCreate) -> Project:
        """Create a new project and persist it to the database."""

        existing_project = await self._get_project_by_name(data.name)
        if existing_project is not None:
            raise ValueError(f"Project with name '{data.name}' already exists")

        project = Project(**data.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_project(self, project_id: UUID, data: ProjectUpdate) -> Project | None:
        """Update an existing active project."""

        project = await self.get_project_by_id(project_id)
        if project is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return project

        if "name" in update_data:
            duplicate_project = await self._get_project_by_name(update_data["name"])
            if duplicate_project is not None and duplicate_project.id != project_id:
                raise ValueError(f"Project with name '{update_data['name']}' already exists")

        for field_name, value in update_data.items():
            setattr(project, field_name, value)

        project.updated_at = datetime.now(timezone.utc)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def soft_delete_project(self, project_id: UUID) -> bool:
        """Soft delete a project by marking it inactive."""

        project = await self.get_project_by_id(project_id)
        if project is None:
            return False

        project.is_active = False
        project.updated_at = datetime.now(timezone.utc)
        self.db.add(project)
        await self.db.commit()
        return True

    async def get_projects_by_domain(self, domain: str) -> list[Project]:
        """Return all active projects that match the provided domain."""

        result = await self.db.execute(
            select(Project)
            .where(Project.domain == domain, Project.is_active.is_(True))
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def search_projects(self, query: str) -> list[Project]:
        """Return active projects whose name or description matches the search query."""

        search_term = f"%{query.lower()}%"
        result = await self.db.execute(
            select(Project)
            .where(
                Project.is_active.is_(True),
                or_(
                    func.lower(Project.name).ilike(search_term),
                    func.lower(Project.description).ilike(search_term),
                    func.lower(Project.domain).ilike(search_term),
                ),
            )
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())
