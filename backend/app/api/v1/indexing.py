"""Indexing API endpoints for managing vector indexing."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.search import IndexingResponse, IndexingStatusResponse, CollectionStats
from app.services.project_service import ProjectService
from app.services.rag_service import get_rag_service
from app.services.vector_store_service import get_vector_store_service
from app.utils.pagination import PaginationParams
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter(prefix="/indexing", tags=["indexing"])


@router.post(
    "/projects",
    response_model=IndexingResponse,
    summary="Index All Projects",
    description="Index all active projects into Qdrant vector database.",
    status_code=status.HTTP_200_OK,
)
async def index_all_projects(db: AsyncSession = Depends(get_db)) -> IndexingResponse:
    """
    Index all active projects into the RAG pipeline.

    Steps:
    1. Fetch all active projects from PostgreSQL
    2. Chunk each project into semantic chunks
    3. Generate embeddings for each chunk
    4. Store vectors in Qdrant
    """
    try:
        project_service = ProjectService(db)

        # Use large page_size to fetch all projects at once
        pagination = PaginationParams(page=1, page_size=1000)
        projects, total = await project_service.get_all_projects(
            filters=None, pagination=pagination
        )

        if not projects:
            logger.warning("No projects found to index")
            return IndexingResponse(
                indexed=0,
                failed=0,
                chunks_total=0,
                status="ok",
                details={"message": "No active projects found"},
            )

        logger.info(f"Starting indexing of {len(projects)} projects")

        rag_service = get_rag_service()
        result = await rag_service.index_all_projects(projects)

        logger.info(f"Indexing complete: {result}")

        return IndexingResponse(
            indexed=result["indexed"],
            failed=result["failed"],
            chunks_total=result["chunks_total"],
            status=result["status"],
            details=result.get("details", {}),
        )

    except Exception as exc:
        logger.error(f"Indexing failed: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(exc)}",
        )


@router.post(
    "/projects/{project_id}",
    response_model=IndexingResponse,
    summary="Index Single Project",
    description="Index a single project by ID into Qdrant vector database.",
    status_code=status.HTTP_200_OK,
)
async def index_single_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> IndexingResponse:
    """
    Index a single project into the RAG pipeline.

    Args:
        project_id: UUID of the project to index
    """
    try:
        project_service = ProjectService(db)
        project = await project_service.get_project_by_id(project_id)

        if not project:
            logger.warning(f"Project not found: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        logger.info(f"Indexing project: {project.name} ({project_id})")

        rag_service = get_rag_service()
        chunk_count = await rag_service.index_project(project)

        logger.info(f"Successfully indexed project {project.name}: {chunk_count} chunks")

        return IndexingResponse(
            indexed=1,
            failed=0,
            chunks_total=chunk_count,
            status="ok",
            details={"project_name": project.name},
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to index project {project_id}: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(exc)}",
        )


@router.delete(
    "/projects/{project_id}",
    response_model=dict,
    summary="Delete Project Vectors",
    description="Delete all vectors associated with a project.",
    status_code=status.HTTP_200_OK,
)
async def delete_project_vectors(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete all vectors associated with a project.

    Args:
        project_id: UUID of the project
    """
    try:
        project_service = ProjectService(db)
        project = await project_service.get_project_by_id(project_id)

        if not project:
            logger.warning(f"Project not found: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        logger.info(f"Deleting vectors for project: {project.name} ({project_id})")

        rag_service = get_rag_service()
        await rag_service.delete_project_vectors(str(project_id))

        logger.info(f"Successfully deleted vectors for project {project.name}")

        return {
            "status": "ok",
            "project_id": str(project_id),
            "project_name": project.name,
            "message": f"Vectors deleted for project {project.name}",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to delete vectors for project {project_id}: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(exc)}",
        )


@router.get(
    "/status",
    response_model=IndexingStatusResponse,
    summary="Get Indexing Status",
    description="Get collection statistics from Qdrant.",
    status_code=status.HTTP_200_OK,
)
async def get_indexing_status() -> IndexingStatusResponse:
    """Get statistics about all indexed collections."""
    try:
        vector_store_service = get_vector_store_service()
        stats = await vector_store_service.get_all_collections_stats()

        collections = {}
        for collection_name, collection_data in stats.items():
            if "error" not in collection_data:
                collections[collection_name] = CollectionStats(
                    name=collection_data["name"],
                    vector_count=collection_data["vector_count"],
                    vectors_size=collection_data["vectors_size"],
                    distance_metric=collection_data["distance_metric"],
                )

        logger.info(f"Retrieved indexing status: {len(collections)} collections")

        return IndexingStatusResponse(
            collections=collections,
            status="ok",
        )

    except Exception as exc:
        logger.error(f"Failed to get indexing status: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(exc)}",
        )