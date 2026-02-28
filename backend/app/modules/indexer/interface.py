"""
Indexer Interface - abstract base for text search backends.
Implementations: MemoryIndexer, MeilisearchIndexer, PostgresFTSIndexer
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class IndexedDocument:
    """Document stored in the index."""

    id: str
    url: str
    title: str
    content: str
    metadata: dict[str, Any] | None = None


@dataclass
class SearchResult:
    """Single search hit."""

    id: str
    url: str
    title: str
    snippet: str
    score: float
    metadata: dict[str, Any] | None = None


class IndexerInterface(ABC):
    """Abstract indexer - all implementations must satisfy this."""

    @abstractmethod
    async def index(self, doc: IndexedDocument) -> bool:
        """Index a document. Returns True on success."""
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search the index. Returns ranked results."""
        ...

    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """Remove a document by id."""
        ...
