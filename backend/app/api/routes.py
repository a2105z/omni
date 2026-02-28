"""
API Gateway routes - /search, /health, /crawl, /index.
"""
import json
import time
from urllib.parse import urlparse

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import (
    get_crawler,
    get_parser,
    get_query_understanding,
    get_hybrid_retriever,
    get_reranker,
    get_indexer,
    get_embedder,
    get_vector_store,
    get_source_quality,
    get_context_assembly,
    get_synthesis_service,
    get_followup_service,
    get_image_search_service,
)
from app.api.schemas import CrawlRequest, IndexRequest, SearchRequest, AnswerRequest
from app.core.config import settings
from app.modules.crawler.interface import CrawlerInterface
from app.modules.indexer.interface import IndexedDocument
from app.modules.parser.interface import ParserInterface
from app.modules.query_understanding.service import QueryUnderstandingService
from app.modules.retriever.hybrid import HybridRetriever
from app.modules.reranker.service import RerankerService
from app.modules.source_quality.service import SourceQualityService
from app.modules.context.service import ContextAssemblyService, TextSource, ImageSource
from app.modules.synthesis.service import SynthesisService
from app.modules.followup.service import FollowUpService
from app.modules.image_search.service import ImageSearchService, ImageResult

router = APIRouter()


def _extract_domain(url: str) -> str:
    try:
        host = (urlparse(url).netloc or "").lower()
        return host[4:] if host.startswith("www.") else host or "unknown"
    except Exception:
        return "unknown"


async def _run_search_pipeline(
    query: str,
    limit: int,
    source_quality: SourceQualityService,
    query_understanding: QueryUnderstandingService,
    retriever: HybridRetriever,
    reranker: RerankerService | None,
    mode: str = "general",
):
    """Core search pipeline. Returns (results, processed_meta)."""
    processed = await query_understanding.process(query.strip())
    primary_query = processed.expanded_queries[0] if processed.expanded_queries else processed.normalized

    use_dense = get_embedder() is not None

    results = await retriever.retrieve(primary_query, limit=settings.FIRST_STAGE_COUNT, use_dense=use_dense)

    if reranker is not None:
        try:
            results = reranker.rerank(primary_query, results, top_k=min(limit, settings.RERANK_TOP_K))
        except Exception:
            results = results[:limit]
    else:
        results = results[:limit]

    results = source_quality.apply(results, apply_dedup=True, apply_diversity=True, mode=mode)[:limit]

    return results, {
        "normalized": processed.normalized,
        "intent": processed.intent,
        "corrected": processed.corrected,
        "expanded_count": len(processed.expanded_queries),
        "expanded_queries": processed.expanded_queries,
    }


@router.get("/health")
async def health():
    """Health check for load balancers and monitoring."""
    return {"status": "healthy", "service": "omni"}


@router.get("/search")
async def search_get(
    q: str,
    limit: int = 10,
    query_understanding: QueryUnderstandingService = Depends(get_query_understanding),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    reranker: RerankerService | None = Depends(get_reranker),
    source_quality: SourceQualityService = Depends(get_source_quality),
):
    """GET /search - backward compatibility."""
    if not q or not q.strip():
        return {"query": q, "results": [], "sources": [], "total": 0, "latency_ms": 0, "error": "Empty query"}
    start = time.perf_counter()
    try:
        results, meta = await _run_search_pipeline(
            q.strip(), limit, source_quality,
            query_understanding, retriever, reranker,
            mode="general",
        )
    except Exception as e:
        return {"query": q, "results": [], "sources": [], "total": 0, "latency_ms": 0, "error": str(e)}
    latency_ms = (time.perf_counter() - start) * 1000
    sources = [
        {"id": r.id, "url": r.url, "title": r.title, "snippet": r.snippet, "score": r.score, "domain": _extract_domain(r.url)}
        for r in results
    ]
    return {
        "query": q,
        "results": sources,
        "sources": sources,
        "total": len(sources),
        "latency_ms": round(latency_ms, 2),
        "processed_query": meta,
    }


@router.post("/search")
async def search_post(
    body: SearchRequest,
    query_understanding: QueryUnderstandingService = Depends(get_query_understanding),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    reranker: RerankerService | None = Depends(get_reranker),
    source_quality: SourceQualityService = Depends(get_source_quality),
):
    """
    POST /api/search - Full Phase 2 pipeline.
    Body: { query, mode?, limit?, stream?, filters? }
    Response: { results, total, latency_ms, sources[] }
    Set stream=true for SSE streaming.
    """
    query = (body.query or "").strip()
    if not query:
        return {"query": "", "results": [], "sources": [], "total": 0, "latency_ms": 0, "error": "Empty query"}

    start = time.perf_counter()
    limit = body.limit
    mode = (body.mode or "general").lower()

    try:
        results, meta = await _run_search_pipeline(
            query, limit, source_quality,
            query_understanding, retriever, reranker,
            mode=mode,
        )
    except Exception as e:
        return {"query": query, "results": [], "sources": [], "total": 0, "latency_ms": 0, "error": str(e)}

    latency_ms = (time.perf_counter() - start) * 1000
    sources = [
        {"id": r.id, "url": r.url, "title": r.title, "snippet": r.snippet, "score": r.score, "domain": _extract_domain(r.url)}
        for r in results
    ]

    if body.stream:
        async def sse_stream():
            yield f"data: {json.dumps({'type': 'meta', 'total': len(sources), 'latency_ms': round(latency_ms, 2), 'processed_query': meta})}\n\n"
            for s in sources:
                yield f"data: {json.dumps({'type': 'result', 'source': s})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return StreamingResponse(sse_stream(), media_type="text/event-stream")

    return {
        "query": query,
        "results": sources,
        "sources": sources,
        "total": len(sources),
        "latency_ms": round(latency_ms, 2),
        "processed_query": meta,
        "mode": body.mode,
    }


@router.post("/crawl")
async def crawl_url(
    body: CrawlRequest,
    crawler: CrawlerInterface = Depends(get_crawler),
    parser: ParserInterface = Depends(get_parser),
):
    """Crawl a single URL and return parsed document - for testing."""
    url = body.url
    raw = await crawler.crawl(url)
    if not raw:
        return {"error": "Failed to fetch URL", "url": url}
    doc = await parser.parse(raw["html"], url=url)
    return {"url": url, "document": doc.to_dict()}


@router.post("/index")
async def index_url(
    body: IndexRequest,
    crawler: CrawlerInterface = Depends(get_crawler),
    parser: ParserInterface = Depends(get_parser),
    indexer=Depends(get_indexer),
    vector_store=Depends(get_vector_store),
):
    """
    Crawl URL, parse, index into BM25 + vector store.
    Seeds the search index for retrieval.
    """
    url = body.url
    raw = await crawler.crawl(url)
    if not raw:
        return {"error": "Failed to fetch URL", "url": url, "indexed": False}
    doc = await parser.parse(raw["html"], url=url)
    text = (doc.title + " " + doc.content)[:100_000]
    doc_id = url.replace(":", "_").replace("/", "_")[:200]
    indexed_doc = IndexedDocument(id=doc_id, url=url, title=doc.title, content=doc.content, metadata={"url": url})
    await indexer.index(indexed_doc)
    embedder = get_embedder()
    if embedder is not None:
        try:
            emb = embedder.embed(text)
            await vector_store.add(doc_id, emb, metadata={"url": url, "title": doc.title})
        except Exception:
            pass
    return {"url": url, "indexed": True, "doc_id": doc_id}


@router.post("/answer")
async def answer_stream(
    body: AnswerRequest,
    query_understanding: QueryUnderstandingService = Depends(get_query_understanding),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    reranker: RerankerService | None = Depends(get_reranker),
    source_quality: SourceQualityService = Depends(get_source_quality),
    context_assembly: ContextAssemblyService = Depends(get_context_assembly),
    synthesis: SynthesisService = Depends(get_synthesis_service),
    followup: FollowUpService = Depends(get_followup_service),
    image_search: ImageSearchService = Depends(get_image_search_service),
):
    """
    Phase 3: Full synthesis pipeline.
    Search -> Context assembly -> Citation-aware streaming answer.
    Optional: image search, follow-up generation.
    """
    query = (body.query or "").strip()
    if not query:
        return {"error": "Empty query"}

    mode = (body.mode or "general").lower()
    limit = body.limit

    async def event_stream():
        try:
            # 1. Run search pipeline
            results, meta = await _run_search_pipeline(
                query, limit, source_quality,
                query_understanding, retriever, reranker,
            )
            sources = [
                {"id": r.id, "url": r.url, "title": r.title, "snippet": r.snippet, "score": r.score, "domain": _extract_domain(r.url)}
                for r in results
            ]

            # 2. Image search (parallel)
            image_results: list[ImageResult] = []
            if body.include_images and settings.ENABLE_IMAGE_SEARCH and image_search.is_available():
                image_results = await image_search.search(query)

            # 3. Context assembly
            text_sources = [
                TextSource(source_number=i + 1, url=s["url"], title=s["title"], content=s["snippet"])
                for i, s in enumerate(sources)
            ]
            image_sources = [
                ImageSource(source_number=i + 1, img_url=img.img_url, title=img.title, summary=img.summary)
                for i, img in enumerate(image_results)
            ]
            source_context, image_context = context_assembly.assemble(text_sources, image_sources)

            # 4. Emit meta (SSE)
            yield f"event: meta\ndata: {json.dumps({'sources': sources, 'image_sources': [{'sourceNumber': i + 1, 'imgUrl': img.img_url, 'title': img.title, 'summary': img.summary} for i, img in enumerate(image_results)], 'processed_query': meta})}\n\n"

            # 5. Stream synthesis
            full_response = []
            async for chunk in synthesis.synthesize_stream(query, source_context, image_context, mode=mode):
                full_response.append(chunk)
                yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"

            full_text = "".join(full_response)

            # 6. Follow-up generation (if OpenAI available)
            follow_ups = []
            expanded = meta.get("expanded_queries") or [query]
            if expanded:
                follow_ups = await followup.generate_follow_ups(
                    query=query,
                    previous_response=full_text,
                    enhanced_queries=expanded,
                )
            yield f"event: done\ndata: {json.dumps({'follow_ups': follow_ups})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
