# Phase 1 - Search Engine Pipeline Skeleton

## Structure

```
omni/
├── frontend/          # Next.js (existing Omni UI)
├── backend/           # Python FastAPI (Phase 1 pipeline)
│   └── app/
│       ├── main.py           # API gateway
│       ├── api/              # Routes, deps, schemas
│       ├── core/             # Config, errors
│       └── modules/
│           ├── crawler/      # CrawlerInterface + HttpxCrawler, FirecrawlCrawler
│           ├── parser/       # ParserInterface + BeautifulSoupParser, ReadabilityParser
│           ├── indexer/      # IndexerInterface + MemoryIndexer
│           └── vector_store/ # VectorStoreInterface + ChromaVectorStore, MemoryVectorStore
└── packages/shared/   # Shared TypeScript types
```

## Backend (Python)

### Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

API: http://localhost:8000

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Health |
| GET | /api/health | Health check |
| GET | /api/search?q=... | Search (skeleton) |
| POST | /api/crawl | Crawl URL, body: `{"url": "https://..."}` |

### Pluggable Modules

- **Crawler**: `HttpxCrawler` (default), `FirecrawlCrawler` (if `FIRECRAWL_API_KEY` set)
- **Parser**: `BeautifulSoupParser` (default), `ReadabilityParser` available
- **Indexer**: `MemoryIndexer` (in-memory), Meilisearch/Postgres can be added
- **Vector Store**: `ChromaVectorStore` if chromadb installed, else `MemoryVectorStore`

## Frontend

```bash
npm run dev --workspace=omni-frontend
# or from root: npm run dev
```

Still uses existing Next.js API routes. Backend integration in later phases.
