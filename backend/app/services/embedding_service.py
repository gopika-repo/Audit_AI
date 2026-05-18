import hashlib
import random
import time
import requests
from typing import List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()
settings = get_settings()

NOMIC_EMBEDDING_MODEL = "nomic-embed-text-v1.5"
NOMIC_DIMENSIONS = 768
NOMIC_API_URL = "https://api-atlas.nomic.ai/v1/embedding/text"


class EmbeddingService:
    def __init__(self):
        self.dimensions = NOMIC_DIMENSIONS
        self.model = NOMIC_EMBEDDING_MODEL
        self.use_mock = not bool(getattr(settings, "NOMIC_API_KEY", ""))
        self.provider = "mock" if self.use_mock else "nomic"
        self.api_key = getattr(settings, "NOMIC_API_KEY", "")

        if not self.use_mock:
            logger.info(f"EmbeddingService initialized with Nomic — model: {self.model}")
        else:
            logger.warning("EmbeddingService using MOCK embeddings — set NOMIC_API_KEY in .env")

    def _mock_embed(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for testing."""
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(NOMIC_DIMENSIONS)]

    def _validate_embedding(self, embedding: Optional[List[float]], text: str) -> List[float]:
        """Validate embedding and fall back to mock if invalid."""
        if embedding is None:
            logger.warning("Embedding is None — falling back to mock")
            return self._mock_embed(text)
        if not isinstance(embedding, list):
            logger.warning(f"Embedding is not a list (got {type(embedding)}) — falling back to mock")
            return self._mock_embed(text)
        if len(embedding) == 0:
            logger.warning("Embedding is empty — falling back to mock")
            return self._mock_embed(text)
        if len(embedding) != NOMIC_DIMENSIONS:
            logger.warning(f"Dimension mismatch: expected {NOMIC_DIMENSIONS}, got {len(embedding)} — falling back to mock")
            return self._mock_embed(text)
        return embedding

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text using Nomic API."""
        if not text or not text.strip():
            logger.warning("Empty text — using mock embedding")
            return self._mock_embed("empty")

        if self.use_mock:
            return self._mock_embed(text)

        try:
            response = requests.post(
                NOMIC_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "texts": [text],
                    "task_type": "search_document",
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                embeddings = data.get("embeddings", [])
                if embeddings and len(embeddings) > 0:
                    embedding = list(embeddings[0])
                    return self._validate_embedding(embedding, text)
                else:
                    logger.warning("No embeddings in Nomic response — falling back to mock")
                    return self._mock_embed(text)
            else:
                logger.error(f"Nomic API error {response.status_code}: {response.text}")
                return self._mock_embed(text)

        except Exception as e:
            logger.error(f"Nomic embedding failed: {e} — falling back to mock")
            return self._mock_embed(text)

    def embed_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []

        if self.use_mock:
            return [self._mock_embed(text) for text in texts]

        embeddings = []
        total = len(texts)

        for i in range(0, total, batch_size):
            batch = texts[i: i + batch_size]
            logger.info(f"Embedding batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size} — {len(batch)} texts")

            try:
                # Nomic supports batch embedding natively
                response = requests.post(
                    NOMIC_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "texts": batch,
                        "task_type": "search_document",
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    batch_embeddings = data.get("embeddings", [])
                    for j, embedding in enumerate(batch_embeddings):
                        validated = self._validate_embedding(list(embedding), batch[j])
                        embeddings.append(validated)
                else:
                    logger.error(f"Nomic batch error {response.status_code} — falling back to mock for batch")
                    for text in batch:
                        embeddings.append(self._mock_embed(text))

            except Exception as e:
                logger.error(f"Nomic batch embedding failed: {e} — using mock for batch")
                for text in batch:
                    embeddings.append(self._mock_embed(text))

            time.sleep(0.2)

        logger.info(f"Generated {len(embeddings)} embeddings total")
        return embeddings


_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def init_embedding_service() -> None:
    get_embedding_service()