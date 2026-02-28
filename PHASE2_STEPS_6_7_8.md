# Phase 2 — Steps 6–10 (Complete)

## Step 6: Query Understanding Service

**Location:** `backend/app/modules/query_understanding/`

| Feature | Implementation |
|---------|----------------|
| **Intent classification** | Rule-based: `navigational`, `informational`, `transactional` |
| **Query expansion** | LLM (OpenAI gpt-4o-mini) when `OPENAI_API_KEY` set; else rule-based synonyms |
| **Spell correction** | `pyspellchecker` |
| **Normalization** | Lowercase, strip, tokenize (regex + optional NLTK) |

**Usage:**
```python
from app.modules.query_understanding.service import QueryUnderstandingService
service = QueryUnderstandingService()
processed = await service.process("what is the besst way to learn react")
# processed.intent, processed.normalized, processed.expanded_queries, processed.corrected
```

---

## Step 7: Hybrid Retriever

**Location:** `backend/app/modules/retriever/`

| Component | Implementation |
|------------|----------------|
| **BM25** | `rank_bm25` via `BM25Indexer` |
| **Dense** | `sentence-transformers` + ChromaDB / MemoryVectorStore |
| **Fusion** | Reciprocal Rank Fusion (RRF) with configurable weights |
| **Config** | `first_stage_count`, `bm25_weight`, `dense_weight` in config |

**RRF formula:** `score = 1 / (k + rank + 1)` with `k=60`

---

## Step 8: ML Reranker

**Location:** `backend/app/modules/reranker/`

| Component | Implementation |
|-----------|----------------|
| **Model** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Input** | (query, doc) pairs |
| **Output** | Top 10–20 by relevance score |
| **Optional** | LTR (XGBoost) — stub for future |

---

## Step 9: Source Quality Pipeline

**Location:** `backend/app/modules/source_quality/`

| Feature | Implementation |
|---------|----------------|
| **Domain scoring** | Trusted (.gov, .edu, wikipedia, github, etc.) vs low-quality (blog, medium) |
| **Freshness scoring** | From metadata timestamp if present |
| **Deduplication** | Jaccard similarity on title+snippet (threshold 0.85) |
| **Diversity** | Max N results per domain (default 2) |

---

## Step 10: Search API

**POST /api/search** body:
```json
{ "query": "what is react", "mode": "general", "limit": 10, "stream": false, "filters": null }
```

**Response:** `{ results, sources, total, latency_ms, processed_query, mode }`

**Streaming:** Set `stream: true` for SSE.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search?q=...&limit=10` | Full pipeline (backward compat) |
| POST | `/api/search` | Full pipeline + optional streaming |
| POST | `/api/index` | Crawl URL, index into BM25 + vector store |
| POST | `/api/crawl` | Crawl + parse only |

---

## Config (`backend/app/core/config.py`)

```python
FIRST_STAGE_COUNT: int = 50
RERANK_TOP_K: int = 20
BM25_WEIGHT: float = 0.5
DENSE_WEIGHT: float = 0.5
RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OPENAI_API_KEY: str | None
MAX_RESULTS_PER_DOMAIN: int = 2   # Diversity
DEDUP_THRESHOLD: float = 0.85    # Near-duplicate threshold
```

---

## Seed the Index

Before searching, index some URLs:

```bash
curl -X POST http://localhost:8000/api/index -H "Content-Type: application/json" -d '{"url": "https://en.wikipedia.org/wiki/React_(web_framework)"}'
```

---

## Dependencies

- `rank-bm25` — BM25
- `nltk` — tokenization, stopwords
- `pyspellchecker` — spell correction
- `sentence-transformers` — embeddings + cross-encoder
- `chromadb` — vector store
- `openai` — optional LLM expansion
