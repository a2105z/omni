"""
Vector Store Interface - abstract base for embedding storage.
Implementations: ChromaVectorStore, QdrantVectorStore, PgVectorStore
"""
from abc import ABC, abstractmethod
from typing import Any


class VectorStoreInterface(ABC):
    """Abstract vector store - all implementations must satisfy this."""

    @abstractmethod
    async def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add or upsert a vector with metadata."""
        ...

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter_: dict | None = None,
    ) -> list[dict]:
        """Search by vector. Returns list of {id, score, metadata}."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Remove a vector by id."""
        ...
