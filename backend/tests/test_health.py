"""Tests for health check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test basic health check endpoint."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "latency_ms" in data
    assert "detail" in data
    assert data["detail"] == "API is running"


@pytest.mark.asyncio
async def test_health_check_response_model(client: AsyncClient) -> None:
    """Test health check response model validation."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    assert "status" in data
    assert "latency_ms" in data
    assert "detail" in data
    
    # Verify data types
    assert isinstance(data["status"], str)
    assert isinstance(data["latency_ms"], (int, float))
    assert isinstance(data["detail"], str)


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root API endpoint."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "Welcome to AI Engineering Onboarding System" in data["message"]


@pytest.mark.asyncio
async def test_health_check_db_endpoint_exists(client: AsyncClient) -> None:
    """Test that database health check endpoint exists."""
    response = await client.get("/api/v1/health/db")
    
    # Should return 200 OK (or error response with proper structure)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "latency_ms" in data
    assert "detail" in data


@pytest.mark.asyncio
async def test_health_check_redis_endpoint_exists(client: AsyncClient) -> None:
    """Test that Redis health check endpoint exists."""
    response = await client.get("/api/v1/health/redis")
    
    # Should return 200 OK (may fail due to Redis not running in test)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "latency_ms" in data
    assert "detail" in data


@pytest.mark.asyncio
async def test_health_check_qdrant_endpoint_exists(client: AsyncClient) -> None:
    """Test that Qdrant health check endpoint exists."""
    response = await client.get("/api/v1/health/qdrant")
    
    # Should return 200 OK (may fail due to Qdrant not running in test)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "latency_ms" in data
    assert "detail" in data
