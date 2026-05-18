"""
Vector store service for Qdrant operations and semantic vector storage.
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4

from qdrant_client.models import (
    PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
)

from app.clients.qdrant_client import get_qdrant
from app.core.logging import get_logger

logger = get_logger()

PROJECTS_KNOWLEDGE_COLLECTION = "projects_knowledge"
ENGINEERING_QA_COLLECTION = "engineering_qa"

VECTOR_SIZE = 768
VECTOR_DISTANCE = Distance.COSINE

COLLECTIONS = [PROJECTS_KNOWLEDGE_COLLECTION, ENGINEERING_QA_COLLECTION]


class VectorStoreService:
    """Service for vector database operations using Qdrant."""

    def __init__(self):
        self.client = get_qdrant()

    async def ensure_collections(self) -> None:
        try:
            collections = await self.client.get_collections()
            existing_names = {collection.name for collection in collections.collections}

            for collection_name in COLLECTIONS:
                if collection_name not in existing_names:
                    await self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(size=VECTOR_SIZE, distance=VECTOR_DISTANCE),
                    )
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.debug(f"Collection already exists: {collection_name}")

        except Exception as exc:
            logger.error(f"Failed to ensure collections: {str(exc)}", exc_info=exc)
            raise

    async def upsert_points(
        self, collection_name: str, points: List[PointStruct]
    ) -> bool:
        if not points:
            logger.warning(f"No points to upsert to collection: {collection_name}")
            return True

        try:
            for point in points:
                if point.id is None:
                    point.id = str(uuid4())

            await self.client.upsert(collection_name=collection_name, points=points)
            logger.info(f"Upserted {len(points)} points to collection: {collection_name}")
            return True

        except Exception as exc:
            logger.error(f"Failed to upsert points to {collection_name}: {str(exc)}", exc_info=exc)
            raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filter_obj: Optional[Filter] = None,
    ) -> List[Dict[str, Any]]:
        try:
            # Try new API first (qdrant-client >= 1.7.0)
            try:
                results = await self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=limit,
                    query_filter=filter_obj,
                    with_payload=True,
                )
                points = results.points
            except AttributeError:
                # Fallback to old API (qdrant-client < 1.7.0)
                points = await self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    query_filter=filter_obj,
                    with_payload=True,
                )

            search_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in points
            ]

            logger.debug(f"Search in {collection_name} returned {len(search_results)} results")
            return search_results

        except Exception as exc:
            logger.error(f"Search failed in {collection_name}: {str(exc)}", exc_info=exc)
            raise

    async def delete_points(self, collection_name: str, project_id: str) -> bool:
        try:
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="metadata.project_id",
                        match=MatchValue(value=project_id),
                    )
                ]
            )

            await self.client.delete(
                collection_name=collection_name,
                points_selector=filter_obj
            )

            logger.info(f"Deleted points for project {project_id} from {collection_name}")
            return True

        except Exception as exc:
            logger.error(f"Failed to delete points for project {project_id}: {str(exc)}", exc_info=exc)
            raise

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection_info = await self.client.get_collection(collection_name=collection_name)

            info_dict = {
                "name": collection_name,
                "vector_count": collection_info.points_count,
                "vectors_size": VECTOR_SIZE,
                "distance_metric": VECTOR_DISTANCE.name,
            }

            logger.debug(f"Collection info for {collection_name}: {info_dict}")
            return info_dict

        except Exception as exc:
            logger.error(f"Failed to get collection info for {collection_name}: {str(exc)}", exc_info=exc)
            raise

    async def get_all_collections_stats(self) -> Dict[str, Any]:
        stats = {}

        try:
            for collection_name in COLLECTIONS:
                try:
                    info = await self.get_collection_info(collection_name)
                    stats[collection_name] = info
                except Exception as exc:
                    logger.warning(f"Failed to get stats for {collection_name}: {str(exc)}")
                    stats[collection_name] = {"error": str(exc)}

            return stats

        except Exception as exc:
            logger.error(f"Failed to get collections stats: {str(exc)}", exc_info=exc)
            raise


_vector_store_service: Optional[VectorStoreService] = None


def get_vector_store_service() -> VectorStoreService:
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service


async def init_vector_store_service() -> None:
    service = get_vector_store_service()
    await service.ensure_collections()
    logger.info("Vector store service initialized and collections created")