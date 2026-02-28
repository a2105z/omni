"""
ChromaVectorStore - persistent vector store using ChromaDB.
Falls back to no-op stub if ChromaDB not installed.
"""
from app.modules.vector_store.interface import VectorStoreInterface


class ChromaVectorStore(VectorStoreInterface):
    """ChromaDB-backed vector store."""

    def __init__(self):
        self._collection_name = "omni_docs"
        self._client = None
        self._collection = None

    def _get_collection(self):
        """Lazy init to avoid import at module load."""
        if self._collection is not None:
            return self._collection
        try:
            from app.core.config import settings
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            return self._collection
        except ImportError:
            raise RuntimeError(
                "ChromaDB not installed. Run: pip install chromadb"
            ) from None
        except Exception as e:
            raise RuntimeError(f"ChromaDB init failed: {e}") from e

    async def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> bool:
        try:
            coll = self._get_collection()
            meta = {k: str(v) for k, v in (metadata or {}).items()}
            coll.upsert(
                ids=[id],
                embeddings=[embedding],
                metadatas=[meta],
            )
            return True
        except Exception:
            return False

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter_: dict | None = None,
    ) -> list[dict]:
        try:
            coll = self._get_collection()
            out = coll.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=filter_,
            )
            results = []
            ids = out.get("ids", [[]])[0]
            metadatas = out.get("metadatas", [[]])[0]
            distances = out.get("distances", [[]])[0] if "distances" in out else [0] * len(ids)
            for i, id_ in enumerate(ids):
                results.append({
                    "id": id_,
                    "score": 1.0 - (distances[i] / 2.0) if distances else 0.0,
                    "metadata": metadatas[i] if metadatas else {},
                })
            return results
        except Exception:
            return []

    async def delete(self, id: str) -> bool:
        try:
            coll = self._get_collection()
            coll.delete(ids=[id])
            return True
        except Exception:
            return False
