"""
ML Reranker Service - Step 8.
Cross-encoder reranker (ms-marco-MiniLM-L-6-v2 or BGE-reranker).
Takes (query, doc) pairs, returns top-k by relevance.
"""
from typing import Any

from app.modules.retriever.hybrid import RetrievalResult


class RerankerService:
    """Cross-encoder reranking for (query, doc) pairs."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        """Lazy load cross-encoder model."""
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self._model_name)
            return self._model
        except ImportError as e:
            raise RuntimeError(
                "sentence-transformers required for reranker. pip install sentence-transformers"
            ) from e

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 20,
    ) -> list[RetrievalResult]:
        """
        Rerank results using cross-encoder.
        Input: query + list of RetrievalResult.
        Output: top_k results sorted by relevance score.
        """
        if not results or top_k <= 0:
            return []
        model = self._get_model()
        pairs = [(query, (r.title + " " + r.snippet).strip() or " ") for r in results]
        scores = model.predict(pairs)
        import numpy as np
        if isinstance(scores, np.ndarray):
            scores = scores.tolist()
        elif not isinstance(scores, list):
            scores = [float(scores)] * len(results)
        indexed = list(zip(results, [float(s) for s in scores]))
        indexed.sort(key=lambda x: -x[1])
        return [r for r, _ in indexed[:top_k]]
