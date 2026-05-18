"""Pydantic schemas for search and indexing APIs."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic search."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=5, ge=1, le=100, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional filters (e.g., {\"domain\": \"Agentic AI\"})"
    )


class SemanticSearchResultItem(BaseModel):
    """Individual result item from semantic search."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str = Field(..., description="Project identifier")
    project_name: str = Field(..., description="Project name")
    chunk_type: str = Field(..., description="Type of chunk (overview, tech_stack, domain, etc.)")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., ge=0, description="Semantic similarity score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class SemanticSearchResponse(BaseModel):
    """Response schema for semantic search."""

    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Original search query")
    results: List[SemanticSearchResultItem] = Field(..., description="List of search results")
    total: int = Field(..., ge=0, description="Total number of results")
    search_type: str = Field(default="semantic", description="Type of search performed")


class HybridSearchResultItem(BaseModel):
    """Individual result item from hybrid search."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str = Field(..., description="Project identifier")
    project_name: str = Field(..., description="Project name")
    chunk_type: str = Field(
        default="hybrid", description="Type of chunk or search result"
    )
    content: Optional[str] = Field(None, description="Content snippet")
    score: float = Field(..., ge=0, description="Combined relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    source: str = Field(
        default="hybrid", description="Source of result (semantic, keyword, or hybrid)"
    )


class HybridSearchResponse(BaseModel):
    """Response schema for hybrid search (semantic + keyword)."""

    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Original search query")
    results: List[HybridSearchResultItem] = Field(..., description="List of merged results")
    total: int = Field(..., ge=0, description="Total number of unique results")
    search_type: str = Field(default="hybrid", description="Type of search performed")


class IndexingResponse(BaseModel):
    """Response schema for indexing operations."""

    model_config = ConfigDict(from_attributes=True)

    indexed: int = Field(..., ge=0, description="Number of projects indexed")
    failed: int = Field(default=0, ge=0, description="Number of projects that failed")
    chunks_total: int = Field(..., ge=0, description="Total number of chunks created")
    status: str = Field(..., description="Indexing status (ok, partial, failed)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class CollectionStats(BaseModel):
    """Statistics for a single Qdrant collection."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Collection name")
    vector_count: int = Field(..., ge=0, description="Number of vectors in collection")
    vectors_size: int = Field(..., description="Dimension size of vectors")
    distance_metric: str = Field(..., description="Distance metric used (Cosine, etc.)")


class IndexingStatusResponse(BaseModel):
    """Response schema for indexing status endpoint."""

    model_config = ConfigDict(from_attributes=True)

    collections: Dict[str, CollectionStats] = Field(
        ..., description="Statistics for each collection"
    )
    status: str = Field(..., description="Overall status")


class ProjectFilter(BaseModel):
    """Optional filters for search."""

    model_config = ConfigDict(from_attributes=True)

    domain: Optional[str] = Field(None, description="Filter by project domain")
    ai_category: Optional[str] = Field(None, description="Filter by AI category")
