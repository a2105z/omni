"""
BM25Indexer - BM25 text retrieval using rank_bm25.
Implements IndexerInterface with proper BM25 scoring.
"""
import re
import uuid
from app.modules.indexer.interface import IndexerInterface, IndexedDocument, SearchResult


def _tokenize(text: str) -> list[str]:
    """Simple tokenization for BM25."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


class BM25Indexer(IndexerInterface):
    """BM25-ranked text index."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._k1 = k1
        self._b = b
        self._docs: list[IndexedDocument] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25 = None

    async def index(self, doc: IndexedDocument) -> bool:
        doc_id = doc.id or str(uuid.uuid4())
        d = IndexedDocument(
            id=doc_id,
            url=doc.url,
            title=doc.title,
            content=doc.content,
            metadata=doc.metadata or {},
        )
        self._docs.append(d)
        self._tokenized_corpus.append(
            _tokenize(d.title + " " + d.content)
        )
        self._bm25 = None
        return True

    def _ensure_bm25(self) -> None:
        if self._bm25 is not None or not self._tokenized_corpus:
            return
        try:
            from rank_bm25 import BM25Okapi
            self._bm25 = BM25Okapi(self._tokenized_corpus)
        except ImportError:
            self._bm25 = None

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if not self._docs:
            return []
        self._ensure_bm25()
        if self._bm25 is None:
            return []
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []
        scores = self._bm25.get_scores(q_tokens)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: -x[1])
        results = []
        for idx, score in indexed[:limit]:
            if score <= 0:
                continue
            doc = self._docs[idx]
            content = doc.title + " " + doc.content
            pos = content.lower().find(q_tokens[0])
            start = max(0, pos - 50)
            end = min(len(content), pos + 100)
            snippet = "..." + content[start:end] + "..."
            results.append(
                SearchResult(
                    id=doc.id,
                    url=doc.url,
                    title=doc.title,
                    snippet=snippet,
                    score=float(score),
                    metadata=doc.metadata,
                )
            )
        return results

    async def delete(self, doc_id: str) -> bool:
        for i, d in enumerate(self._docs):
            if d.id == doc_id:
                self._docs.pop(i)
                self._tokenized_corpus.pop(i)
                self._bm25 = None
                return True
        return False
