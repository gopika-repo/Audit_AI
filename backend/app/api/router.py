"""
API router setup - aggregates all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import health, projects, indexing, search, chat

router = APIRouter(prefix="/api/v1")

# Include health check routes
router.include_router(health.router)

# Include projects routes
router.include_router(projects.router)

# Include indexing routes
router.include_router(indexing.router)

# Include search routes
router.include_router(search.router)
# Include chat routes
router.include_router(chat.router)
