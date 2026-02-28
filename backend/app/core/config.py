"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Crawler
    CRAWLER_USER_AGENT: str = "OmniBot/1.0 (+https://github.com/omni)"
    CRAWLER_REQUEST_DELAY: float = 1.0
    CRAWLER_MAX_PAGES_PER_DOMAIN: int = 10

    # Indexer
    INDEXER_BACKEND: str = "memory"  # memory | meilisearch | postgres
    MEILISEARCH_URL: str = "http://localhost:7700"

    # Vector Store
    VECTOR_STORE_BACKEND: str = "chroma"  # chroma | qdrant | pgvector
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Firecrawl (optional)
    FIRECRAWL_API_KEY: str | None = None

    # OpenAI (optional - for LLM query expansion)
    OPENAI_API_KEY: str | None = None

    # Query Understanding & Retrieval
    FIRST_STAGE_COUNT: int = 50
    RERANK_TOP_K: int = 20
    BM25_WEIGHT: float = 0.5
    DENSE_WEIGHT: float = 0.5
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Source Quality (Step 9)
    MAX_RESULTS_PER_DOMAIN: int = 2
    DEDUP_THRESHOLD: float = 0.85

    # Phase 3: Synthesis & AI
    CONTEXT_MAX_TOKENS: int = 12_000
    SYNTHESIS_MODEL: str = "gpt-4o-mini"
    FOLLOWUP_NUM_QUERIES: int = 5
    BRAVE_API_KEY: str | None = None
    IMAGE_SEARCH_MAX_RESULTS: int = 5
    ENABLE_IMAGE_SEARCH: bool = True

    # Rate limiting (Step 20)
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60


settings = Settings()
