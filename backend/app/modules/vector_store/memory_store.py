"""
MemoryVectorStore - in-memory vector store for Phase 1 development.
Use when ChromaDB is not installed or for quick testing.
"""
from app.modules.vector_store.interface import VectorStoreInterface


class MemoryVectorStore(VectorStoreInterface):
    """In-memory stub - no persistence, no real similarity."""

    def __init__(self):
        self._vectors: dict[str, tuple[list[float], dict]] = {}

    async def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> bool:
        self._vectors[id] = (embedding, metadata or {})
        return True

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter_: dict | None = None,
    ) -> list[dict]:
        if not self._vectors:
            return []
        # Naive dot-product similarity
        scored = []
        for vid, (vec, meta) in self._vectors.items():
            if len(vec) != len(query_embedding):
                continue
            score = sum(a * b for a, b in zip(vec, query_embedding))
            scored.append((score, vid, meta))
        scored.sort(key=lambda x: -x[0])
        return [
            {"id": vid, "score": float(s), "metadata": meta}
            for s, vid, meta in scored[:limit]
        ]

    async def delete(self, id: str) -> bool:
        if id in self._vectors:
            del self._vectors[id]
            return True
        return False
