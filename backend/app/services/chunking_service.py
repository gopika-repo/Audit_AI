"""
Chunking service for splitting project content into semantically meaningful chunks.
"""

from typing import List

from app.models.project import Project
from app.core.logging import get_logger

logger = get_logger()

# Chunking configuration
CHUNK_SIZE = 512  # approximate tokens
CHUNK_OVERLAP = 50  # approximate tokens


def _count_tokens_approximate(text: str) -> int:
    """
    Approximate token count using word count.
    
    Uses the rough heuristic: 1 token ≈ 0.75 words
    """
    word_count = len(text.split())
    return int(word_count / 0.75)


class Chunk:
    """Represents a single chunk of project content."""

    def __init__(
        self,
        content: str,
        chunk_type: str,
        project_id: str,
        project_name: str,
        domain: str,
        metadata: dict = None,
    ):
        self.content = content
        self.chunk_type = chunk_type
        self.project_id = project_id
        self.project_name = project_name
        self.domain = domain
        self.metadata = metadata or {}

    def to_dict(self):
        """Convert chunk to dictionary."""
        return {
            "content": self.content,
            "chunk_type": self.chunk_type,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "domain": self.domain,
            "metadata": self.metadata,
        }


class ChunkingService:
    """Service for chunking project content."""

    @staticmethod
    def _count_tokens(text: str) -> int:
        """Count tokens in text using approximate calculation."""
        return _count_tokens_approximate(text)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """
        Split text into chunks based on approximate token count.

        Uses word count as proxy for token count (1 token ≈ 0.75 words).

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in approximate tokens
            overlap: Number of tokens to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Convert token sizes to word counts
        words_per_chunk = int(chunk_size * 0.75)
        overlap_words = int(overlap * 0.75)
        overlap_words = max(1, min(overlap_words, words_per_chunk // 4))

        words = text.split()

        if len(words) <= words_per_chunk:
            return [text]

        chunks = []
        start = 0

        while start < len(words):
            end = min(start + words_per_chunk, len(words))
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))

            # Move start position with overlap
            start = end - overlap_words

        return chunks

    @staticmethod
    def chunk_project(project: Project) -> List[Chunk]:
        """
        Chunk a project into distinct semantic chunks.

        Args:
            project: Project model instance

        Returns:
            List of Chunk objects
        """
        project_id = str(project.id)
        name = project.name or ""
        description = project.description or ""
        domain = project.domain or ""
        ai_category = project.ai_category or "General AI"
        tech_stack = project.tech_stack or {}

        languages = tech_stack.get("languages", []) if isinstance(tech_stack, dict) else []
        frameworks = tech_stack.get("frameworks", []) if isinstance(tech_stack, dict) else []
        tools = tech_stack.get("tools", []) if isinstance(tech_stack, dict) else []

        languages = [str(item) for item in languages if item is not None]
        frameworks = [str(item) for item in frameworks if item is not None]
        tools = [str(item) for item in tools if item is not None]

        tech_stack_string = (
            f"Languages: {', '.join(languages)}. "
            f"Frameworks: {', '.join(frameworks)}. "
            f"Tools: {', '.join(tools)}."
        )

        chunks = [
            Chunk(
                content=f"{name}: {description}",
                chunk_type="overview",
                project_id=project_id,
                project_name=name,
                domain=domain,
                metadata={"type": "overview", "project_id": project_id, "project_name": name, "domain": domain},
            ),
            Chunk(
                content=f"{name} uses: {tech_stack_string}",
                chunk_type="tech_stack",
                project_id=project_id,
                project_name=name,
                domain=domain,
                metadata={"type": "tech_stack", "project_id": project_id, "project_name": name, "domain": domain},
            ),
            Chunk(
                content=f"{name} is a {domain} project focused on {ai_category}",
                chunk_type="domain",
                project_id=project_id,
                project_name=name,
                domain=domain,
                metadata={"type": "domain", "project_id": project_id, "project_name": name, "domain": domain},
            ),
            Chunk(
                content=f"{name}: {description}. Domain: {domain}. AI Category: {ai_category}. {tech_stack_string}",
                chunk_type="engineering_context",
                project_id=project_id,
                project_name=name,
                domain=domain,
                metadata={"type": "engineering_context", "project_id": project_id, "project_name": name, "domain": domain},
            ),
        ]

        logger.info(f"Created {len(chunks)} chunks for project: {name}")
        return chunks
