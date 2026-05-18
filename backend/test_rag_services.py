"""
Quick test script for RAG services.
"""
from uuid import uuid4
from datetime import datetime, timezone

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.models.project import Project


def test_chunking():
    """Test chunking service."""
    # Create a mock project
    project = Project(
        id=uuid4(),
        name="Test LangGraph Project",
        description="A project using LangGraph for multi-agent workflows and AI systems",
        domain="Agentic AI",
        ai_category="Multi-Agent Systems",
        tech_stack={"frameworks": ["LangGraph", "LangChain"], "languages": ["Python"]},
        repo_url="https://github.com/example/repo",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Test ChunkingService
    chunking_service = ChunkingService()
    chunks = chunking_service.chunk_project(project)
    
    print(f"[OK] Created {len(chunks)} chunks for project: {project.name}")
    for i, chunk in enumerate(chunks, 1):
        print(f"     Chunk {i}: {chunk.chunk_type} ({len(chunk.content)} chars)")
    
    return True


def test_embedding():
    """Test embedding service."""
    embedding_service = EmbeddingService()
    print(f"[OK] Embedding service initialized (provider: {embedding_service.provider})")
    
    # Test single embedding
    embedding = embedding_service.embed_single("LangGraph workflow")
    print(f"[OK] Generated single embedding: {len(embedding)} dimensions")
    
    # Test batch embedding
    texts = [
        "LangGraph is a framework for building agentic workflows",
        "Computer vision with transformer models",
        "Backend optimization techniques",
    ]
    embeddings = embedding_service.embed_batch(texts)
    print(f"[OK] Generated batch embeddings: {len(embeddings)} embeddings")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing RAG Services")
    print("=" * 60)
    
    print("\n1. Testing ChunkingService...")
    test_chunking()
    
    print("\n2. Testing EmbeddingService...")
    test_embedding()
    
    print("\n" + "=" * 60)
    print("[PASS] All core services working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    main()
