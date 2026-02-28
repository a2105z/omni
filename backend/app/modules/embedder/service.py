"""
Embedder Service - produces dense vectors for queries and documents.
Used by HybridRetriever for dense retrieval.
"""
from functools import lru_cache


class EmbedderService:
    """Get embeddings via sentence-transformers or fallback."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        """Lazy load sentence-transformers model."""
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            return self._model
        except ImportError as e:
            raise RuntimeError(
                "sentence-transformers not installed. Run: pip install sentence-transformers"
            ) from e

    def embed(self, text: str) -> list[float]:
        """Single text to embedding."""
        model = self._get_model()
        return model.encode(text, convert_to_numpy=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed for efficiency."""
        if not texts:
            return []
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]
