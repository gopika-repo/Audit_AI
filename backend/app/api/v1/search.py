"""Search API endpoints for semantic and hybrid search."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.project import ProjectResponse
from app.schemas.search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
    HybridSearchResponse,
    HybridSearchResultItem,
)
from app.services.rag_service import get_rag_service
from app.services.project_service import ProjectService
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    summary="Semantic Search",
    description="Search for projects using semantic similarity.",
    status_code=status.HTTP_200_OK,
)
async def semantic_search(
    request: SemanticSearchRequest,
) -> SemanticSearchResponse:
    """
    Perform semantic search using vector embeddings.

    This endpoint:
    1. Embeds the search query
    2. Searches for similar vectors in Qdrant
    3. Returns ranked results with similarity scores

    Args:
        request: SemanticSearchRequest with query and optional filters

    Returns:
        SemanticSearchResponse with search results

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Semantic search: {request.query}")

        # Perform semantic search
        rag_service = get_rag_service()
        search_results = await rag_service.search_similar(
            query=request.query,
            limit=request.limit,
            filters=request.filters or {},
        )

        # Convert to response items
        result_items = [
            SemanticSearchResultItem(
                project_id=result.project_id,
                project_name=result.project_name,
                chunk_type=result.chunk_type,
                content=result.content,
                score=result.score,
                metadata=result.metadata,
            )
            for result in search_results
        ]

        logger.info(f"Semantic search returned {len(result_items)} results")

        return SemanticSearchResponse(
            query=request.query,
            results=result_items,
            total=len(result_items),
            search_type="semantic",
        )

    except Exception as exc:
        logger.error(f"Semantic search failed: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(exc)}",
        )


@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
    summary="Hybrid Search",
    description="Combine semantic and keyword search results.",
    status_code=status.HTTP_200_OK,
)
async def hybrid_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> HybridSearchResponse:
    """
    Perform hybrid search combining semantic + keyword search.

    This endpoint:
    1. Performs semantic search using vector embeddings
    2. Performs keyword search on PostgreSQL
    3. Merges and deduplicates results
    4. Ranks by semantic score

    Args:
        request: SemanticSearchRequest with query and optional filters
        db: Database session

    Returns:
        HybridSearchResponse with merged results

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Hybrid search: {request.query}")

        # Step 1: Perform semantic search
        rag_service = get_rag_service()
        semantic_results = await rag_service.search_similar(
            query=request.query,
            limit=request.limit,
            filters=request.filters or {},
        )

        # Step 2: Perform keyword search
        project_service = ProjectService(db)
        from app.schemas.project import ProjectFilter
        from app.utils.pagination import PaginationParams

        keyword_filter = ProjectFilter(
            search=request.query,
            domain=request.filters.get("domain") if request.filters else None,
        )
        keyword_pagination = PaginationParams(page=1, page_size=request.limit)

        keyword_projects, _ = await project_service.get_all_projects(
            filters=keyword_filter,
            pagination=keyword_pagination,
        )

        # Step 3: Merge results (deduplicate by project_id)
        merged_results: Dict[str, HybridSearchResultItem] = {}

        # Add semantic results first (they have scores)
        for result in semantic_results:
            key = result.project_id
            merged_results[key] = HybridSearchResultItem(
                project_id=result.project_id,
                project_name=result.project_name,
                chunk_type=result.chunk_type,
                content=result.content,
                score=result.score,
                metadata=result.metadata,
                source="semantic",
            )

        # Add keyword results (deduplicate, keep semantic score if exists)
        for project in keyword_projects:
            key = str(project.id)
            if key not in merged_results:
                merged_results[key] = HybridSearchResultItem(
                    project_id=str(project.id),
                    project_name=project.name,
                    chunk_type="project",
                    content=project.description[:200],  # Snippet
                    score=0.5,  # Default keyword score
                    metadata={"domain": project.domain, "ai_category": project.ai_category},
                    source="keyword",
                )

        # Step 4: Sort by score (descending)
        sorted_results = sorted(
            merged_results.values(),
            key=lambda x: x.score,
            reverse=True,
        )

        logger.info(f"Hybrid search returned {len(sorted_results)} unique results")

        return HybridSearchResponse(
            query=request.query,
            results=sorted_results,
            total=len(sorted_results),
            search_type="hybrid",
        )

    except Exception as exc:
        logger.error(f"Hybrid search failed: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(exc)}",
        )


@router.get(
    "/projects",
    response_model=dict,
    summary="Keyword Search Projects",
    description="Search projects by keyword (existing Phase 2 endpoint).",
    status_code=status.HTTP_200_OK,
)
async def search_projects_keyword(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Keyword search on projects (Phase 2 functionality).

    Args:
        q: Search query
        limit: Maximum number of results
        db: Database session

    Returns:
        Dictionary with search results
    """
    try:
        logger.info(f"Keyword search: {q}")

        project_service = ProjectService(db)
        from app.schemas.project import ProjectFilter
        from app.utils.pagination import PaginationParams

        search_filter = ProjectFilter(search=q)
        pagination = PaginationParams(page=1, page_size=limit)

        projects, total = await project_service.get_all_projects(
            filters=search_filter,
            pagination=pagination,
        )

        result_items = [ProjectResponse.model_validate(project) for project in projects]

        logger.info(f"Keyword search returned {len(result_items)} results")

        return {
            "query": q,
            "results": [item.model_dump() for item in result_items],
            "total": total,
            "search_type": "keyword",
        }

    except Exception as exc:
        logger.error(f"Keyword search failed: {str(exc)}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(exc)}",
        )
