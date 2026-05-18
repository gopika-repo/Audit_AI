"""
RAG (Retrieval Augmented Generation) service orchestrating the complete RAG pipeline.
"""

from typing import List, Dict, Any
from uuid import uuid4

from qdrant_client.models import PointStruct

from app.models.project import Project
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import get_embedding_service
from app.services.vector_store_service import (
    get_vector_store_service,
    PROJECTS_KNOWLEDGE_COLLECTION,
)
from app.core.logging import get_logger

logger = get_logger()


class SearchResult:
    """Represents a search result."""

    def __init__(
        self,
        project_id: str,
        project_name: str,
        chunk_type: str,
        content: str,
        score: float,
        metadata: Dict[str, Any],
    ):
        self.project_id = project_id
        self.project_name = project_name
        self.chunk_type = chunk_type
        self.content = content
        self.score = score
        self.metadata = metadata

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "chunk_type": self.chunk_type,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }


class RAGService:
    """Orchestrates chunking, embedding, and vector storage for RAG pipeline."""

    def __init__(self):
        """Initialize RAG service with dependencies."""
        self.chunking_service = ChunkingService()
        self.embedding_service = get_embedding_service()
        self.vector_store_service = get_vector_store_service()

    async def index_project(self, project: Project) -> int:
        """
        Index a single project into the RAG pipeline.

        Args:
            project: Project model to index

        Returns:
            Number of chunks indexed
        """
        project_id = str(project.id)
        project_name = project.name

        try:
            # Step 1: Chunk the project
            chunks = self.chunking_service.chunk_project(project)
            logger.info(f"Chunked project {project_name} into {len(chunks)} chunks")

            # Step 2: Extract chunk contents and embed
            chunk_contents = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_batch(chunk_contents)
            logger.info(f"Generated {len(embeddings)} embeddings for project {project_name}")

            # Step 3: Build PointStructs with metadata
            points = []
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "content": chunk.content,
                        "chunk_type": chunk.chunk_type,
                        "metadata": chunk.metadata,
                        "project_id": project_id,
                        "project_name": project_name,
                        "domain": chunk.domain,
                    },
                )
                points.append(point)

            # Step 4: Upsert to vector store
            await self.vector_store_service.upsert_points(
                PROJECTS_KNOWLEDGE_COLLECTION, points
            )
            logger.info(
                f"Successfully indexed project {project_name} with {len(chunks)} chunks"
            )

            return len(chunks)

        except Exception as exc:
            logger.error(f"Failed to index project {project_name}: {str(exc)}", exc_info=exc)
            raise

    async def index_all_projects(self, projects: List[Project]) -> Dict[str, Any]:
        """
        Index all projects into the RAG pipeline.

        Args:
            projects: List of projects to index

        Returns:
            Summary dictionary with indexing stats
        """
        indexed_count = 0
        total_chunks = 0
        failed_projects = []

        logger.info(f"Starting batch indexing of {len(projects)} projects")

        for project in projects:
            try:
                chunk_count = await self.index_project(project)
                indexed_count += 1
                total_chunks += chunk_count
            except Exception as exc:
                logger.error(f"Failed to index project {project.name}: {str(exc)}")
                failed_projects.append({"name": project.name, "error": str(exc)})

        result = {
            "indexed": indexed_count,
            "failed": len(failed_projects),
            "chunks_total": total_chunks,
            "status": "ok" if len(failed_projects) == 0 else "partial",
            "details": {
                "failed_projects": failed_projects,
            },
        }

        logger.info(f"Batch indexing complete: {indexed_count}/{len(projects)} projects indexed")
        return result

    async def search_similar(
        self,
        query: str,
        limit: int = 10,
        filters: Dict[str, Any] = None,
    ) -> List[SearchResult]:
        """
        Search for semantically similar content.

        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters (e.g., {"domain": "Agentic AI"})

        Returns:
            List of SearchResult objects
        """
        filters = filters or {}

        try:
            # Step 1: Embed the query
            query_embedding = self.embedding_service.embed_single(query)
            logger.info(f"Generated embedding for query: {query[:50]}...")

            # Step 2: Search in vector store
            search_results = await self.vector_store_service.search(
                PROJECTS_KNOWLEDGE_COLLECTION,
                query_vector=query_embedding,
                limit=limit,
                filter_obj=None,  # Filter logic can be added here if needed
            )

            # Step 3: Apply post-search filters and convert to SearchResult objects
            results = []
            for result in search_results:
                payload = result["payload"]
                metadata = payload.get("metadata", {})

                # Apply domain filter if provided
                if filters.get("domain"):
                    if metadata.get("domain") != filters["domain"]:
                        continue

                search_result = SearchResult(
                    project_id=payload.get("project_id"),
                    project_name=payload.get("project_name"),
                    chunk_type=payload.get("chunk_type"),
                    content=payload.get("content"),
                    score=result["score"],
                    metadata=metadata,
                )
                results.append(search_result)

            logger.info(f"Found {len(results)} search results for query: {query[:50]}...")
            return results

        except Exception as exc:
            logger.error(f"Search failed for query '{query}': {str(exc)}", exc_info=exc)
            raise

    async def delete_project_vectors(self, project_id: str) -> bool:
        """
        Delete all vectors associated with a project.

        Args:
            project_id: ID of the project

        Returns:
            True if successful
        """
        try:
            await self.vector_store_service.delete_points(
                PROJECTS_KNOWLEDGE_COLLECTION, project_id
            )
            logger.info(f"Deleted vectors for project {project_id}")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete vectors for project {project_id}: {str(exc)}")
            raise


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """
    Get or create the singleton RAGService instance.

    Returns:
        RAGService: Singleton instance
    """
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()

    return _rag_service
