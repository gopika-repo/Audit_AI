"""Projects API endpoints for CRUD and discovery operations."""

from __future__ import annotations

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectFilter,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService
from app.utils.pagination import PaginationParams, calculate_total_pages

router = APIRouter(prefix="/projects", tags=["projects"])


def _build_list_response(items: list[ProjectResponse], page: int, page_size: int) -> ProjectListResponse:
    """Build a paginated response wrapper for project lists."""

    total = len(items)
    total_pages = calculate_total_pages(total, page_size)
    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List Projects",
    description="List active projects with pagination and optional filters.",
)
async def list_projects(
    filters: ProjectFilter = Depends(),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """Return a paginated list of active projects."""

    service = ProjectService(db)
    items, total = await service.get_all_projects(filters, pagination)
    response_items = [ProjectResponse.model_validate(project) for project in items]
    return ProjectListResponse(
        items=response_items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=calculate_total_pages(total, pagination.page_size),
    )


@router.get(
    "/search",
    response_model=List[ProjectResponse],
    summary="Search Projects",
    description="Search active projects by name, description, or domain.",
)
async def search_projects(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectResponse]:
    """Search active projects by name, description, or domain."""

    service = ProjectService(db)
    projects = await service.search_projects(q)
    return [ProjectResponse.model_validate(project) for project in projects]


@router.get(
    "/domain/{domain}",
    response_model=ProjectListResponse,
    summary="Get Projects by Domain",
    description="Return all active projects for a specific domain.",
)
async def get_projects_by_domain(
    domain: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """Return active projects for the requested domain."""

    service = ProjectService(db)
    projects = await service.get_projects_by_domain(domain)
    response_items = [ProjectResponse.model_validate(project) for project in projects]
    return _build_list_response(response_items, page=1, page_size=max(len(response_items), 1))


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get Project",
    description="Get a single active project by UUID.",
)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Return a single project by UUID."""

    service = ProjectService(db)
    project = await service.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project",
    description="Create a new project.",
)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Create a new project and return the stored record."""

    service = ProjectService(db)
    try:
        project = await service.create_project(project_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ProjectResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update Project",
    description="Update an existing project.",
)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Update an existing project by UUID."""

    service = ProjectService(db)
    try:
        project = await service.update_project(project_id, project_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete Project",
    description="Soft delete a project by marking it inactive.",
)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Soft delete a project by UUID."""

    service = ProjectService(db)
    deleted = await service.soft_delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
