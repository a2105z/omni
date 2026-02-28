"""
MemoryIndexer - in-memory text search for Phase 1.
Simple keyword matching; replace with Meilisearch/Elasticsearch for production.
"""
import re
import uuid
from app.modules.indexer.interface import IndexerInterface, IndexedDocument, SearchResult


class MemoryIndexer(IndexerInterface):
    """In-memory index - for development and testing."""

    def __init__(self):
        self._docs: dict[str, IndexedDocument] = {}

    async def index(self, doc: IndexedDocument) -> bool:
        doc_id = doc.id or str(uuid.uuid4())
        self._docs[doc_id] = IndexedDocument(
            id=doc_id,
            url=doc.url,
            title=doc.title,
            content=doc.content,
            metadata=doc.metadata or {},
        )
        return True

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        q = query.lower().strip()
        if not q:
            return []
        terms = re.findall(r"\w+", q)
        scored: list[tuple[float, IndexedDocument]] = []
        for doc in self._docs.values():
            text = (doc.title + " " + doc.content).lower()
            score = 0.0
            for t in terms:
                score += text.count(t)
            if score > 0:
                # Snippet: first occurrence context
                idx = text.find(terms[0])
                start = max(0, idx - 40)
                end = min(len(text), idx + 80)
                snippet = "..." + text[start:end] + "..."
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [
            SearchResult(
                id=d.id,
                url=d.url,
                title=d.title,
                snippet=snippet,
                score=score,
                metadata=d.metadata,
            )
            for score, d in scored[:limit]
        ]

    async def delete(self, doc_id: str) -> bool:
        if doc_id in self._docs:
            del self._docs[doc_id]
            return True
        return False
