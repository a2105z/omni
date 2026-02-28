"""
Dependency injection - provides pluggable module instances.
"""
from functools import lru_cache

from app.core.config import settings
from app.modules.crawler.interface import CrawlerInterface
from app.modules.crawler.firecrawl_crawler import FirecrawlCrawler
from app.modules.crawler.httpx_crawler import HttpxCrawler
from app.modules.embedder.service import EmbedderService
from app.modules.indexer.interface import IndexerInterface
from app.modules.indexer.bm25_indexer import BM25Indexer
from app.modules.indexer.memory_indexer import MemoryIndexer
from app.modules.parser.interface import ParserInterface
from app.modules.parser.beautifulsoup_parser import BeautifulSoupParser
from app.modules.query_understanding.service import QueryUnderstandingService
from app.modules.reranker.service import RerankerService
from app.modules.retriever.hybrid import HybridRetriever
from app.modules.source_quality.service import SourceQualityService
from app.modules.vector_store.interface import VectorStoreInterface
from app.modules.vector_store.chroma_store import ChromaVectorStore


@lru_cache
def get_crawler() -> CrawlerInterface:
    """Return crawler implementation (pluggable)."""
    if settings.FIRECRAWL_API_KEY:
        return FirecrawlCrawler()
    return HttpxCrawler()


@lru_cache
def get_parser() -> ParserInterface:
    """Return parser implementation."""
    return BeautifulSoupParser()


@lru_cache
def get_indexer() -> IndexerInterface:
    """Return indexer - BM25 if available, else memory."""
    try:
        from rank_bm25 import BM25Okapi
        return BM25Indexer()
    except ImportError:
        return MemoryIndexer()


@lru_cache
def get_vector_store() -> VectorStoreInterface:
    """Return vector store implementation (pluggable)."""
    try:
        return ChromaVectorStore()
    except (ImportError, RuntimeError):
        from app.modules.vector_store.memory_store import MemoryVectorStore
        return MemoryVectorStore()


@lru_cache
def get_embedder() -> EmbedderService | None:
    """Return embedder - for dense retrieval. None if sentence-transformers not installed."""
    try:
        from sentence_transformers import SentenceTransformer
        return EmbedderService(model_name=settings.EMBEDDING_MODEL)
    except ImportError:
        return None


@lru_cache
def get_query_understanding() -> QueryUnderstandingService:
    """Return query understanding service."""
    return QueryUnderstandingService(use_spell_check=True, use_expansion=True)


@lru_cache
def get_reranker() -> RerankerService | None:
    """Return reranker - cross-encoder. None if sentence-transformers not installed."""
    try:
        from sentence_transformers import CrossEncoder
        return RerankerService(model_name=settings.RERANKER_MODEL)
    except ImportError:
        return None


@lru_cache
def get_source_quality() -> SourceQualityService:
    """Return source quality pipeline."""
    return SourceQualityService(
        max_per_domain=settings.MAX_RESULTS_PER_DOMAIN,
        dedup_threshold=settings.DEDUP_THRESHOLD,
    )


@lru_cache
def get_hybrid_retriever() -> HybridRetriever:
    """Return hybrid retriever (BM25 + Dense + RRF). Dense disabled if embedder unavailable."""
    embedder = get_embedder()
    return HybridRetriever(
        indexer=get_indexer(),
        vector_store=get_vector_store(),
        embedder=embedder,
        first_stage_count=settings.FIRST_STAGE_COUNT,
        bm25_weight=settings.BM25_WEIGHT,
        dense_weight=settings.DENSE_WEIGHT,
    )


# Phase 3 deps
from app.modules.context.service import ContextAssemblyService
from app.modules.synthesis.service import SynthesisService
from app.modules.followup.service import FollowUpService
from app.modules.image_search.service import ImageSearchService


@lru_cache
def get_context_assembly() -> ContextAssemblyService:
    return ContextAssemblyService(max_tokens=settings.CONTEXT_MAX_TOKENS)


@lru_cache
def get_synthesis_service() -> SynthesisService:
    return SynthesisService(model=settings.SYNTHESIS_MODEL)


@lru_cache
def get_followup_service() -> FollowUpService:
    return FollowUpService(num_queries=settings.FOLLOWUP_NUM_QUERIES)


@lru_cache
def get_image_search_service() -> ImageSearchService:
    return ImageSearchService(
        max_results=settings.IMAGE_SEARCH_MAX_RESULTS,
        api_key=settings.BRAVE_API_KEY,
    )
