"""
Hybrid Retriever - Step 7.
BM25 + Dense retrieval with Reciprocal Rank Fusion (RRF).
"""
from dataclasses import dataclass

from app.modules.indexer.interface import IndexerInterface, SearchResult
from app.modules.vector_store.interface import VectorStoreInterface


@dataclass
class RetrievalResult:
    """Single result from hybrid retrieval."""

    id: str
    url: str
    title: str
    snippet: str
    score: float
    metadata: dict


class HybridRetriever:
    """
    Hybrid retrieval: BM25 + Dense vectors, fused with RRF.
    """

    RRF_K = 60

    def __init__(
        self,
        indexer: IndexerInterface,
        vector_store: VectorStoreInterface,
        embedder=None,
        first_stage_count: int = 50,
        bm25_weight: float = 0.5,
        dense_weight: float = 0.5,
    ):
        self._indexer = indexer
        self._vector_store = vector_store
        self._embedder = embedder
        self._first_stage_count = first_stage_count
        self._bm25_weight = bm25_weight
        self._dense_weight = dense_weight

    @staticmethod
    def _rrf_score(rank: int, k: int = 60) -> float:
        """Reciprocal Rank Fusion score."""
        return 1.0 / (k + rank + 1)

    async def retrieve(
        self,
        query: str,
        limit: int = 20,
        use_dense: bool = True,
    ) -> list[RetrievalResult]:
        """
        Retrieve documents: BM25 + optional dense, then RRF fusion.
        """
        all_doc_ids: set[str] = set()
        rrf_scores: dict[str, float] = {}

        # BM25 retrieval
        bm25_results = await self._indexer.search(
            query, limit=self._first_stage_count
        )
        for rank, r in enumerate(bm25_results):
            all_doc_ids.add(r.id)
            rrf_scores[r.id] = rrf_scores.get(r.id, 0) + self._bm25_weight * self._rrf_score(rank)
            if r.id not in all_doc_ids:
                all_doc_ids.add(r.id)

        # Dense retrieval (if embedder available and vector store has data)
        if use_dense and self._embedder is not None:
            try:
                q_emb = self._embedder.embed(query)
                dense_results = await self._vector_store.search(
                    q_emb, limit=self._first_stage_count
                )
                for rank, hit in enumerate(dense_results):
                    doc_id = hit.get("id", "")
                    if doc_id:
                        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + self._dense_weight * self._rrf_score(rank)
                        all_doc_ids.add(doc_id)
            except Exception:
                pass

        # Build doc lookup from BM25 (has full SearchResult)
        doc_by_id: dict[str, SearchResult] = {r.id: r for r in bm25_results}

        # For dense-only docs we need metadata - vector_store returns {id, score, metadata}
        # We may not have title/url/snippet for dense-only. Use placeholder if missing.
        for doc_id in all_doc_ids:
            if doc_id not in doc_by_id:
                doc_by_id[doc_id] = SearchResult(
                    id=doc_id,
                    url=doc_id,
                    title="",
                    snippet="",
                    score=0,
                    metadata={},
                )

        # Sort by fused score
        scored = [(doc_id, rrf_scores.get(doc_id, 0)) for doc_id in all_doc_ids]
        scored.sort(key=lambda x: -x[1])

        out = []
        for doc_id, score in scored[:limit]:
            sr = doc_by_id.get(doc_id)
            if not sr:
                continue
            out.append(
                RetrievalResult(
                    id=sr.id,
                    url=sr.url,
                    title=sr.title,
                    snippet=sr.snippet,
                    score=score,
                    metadata=sr.metadata or {},
                )
            )
        return out
