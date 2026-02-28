"""Request/response schemas."""
from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """POST /crawl body."""

    url: str


class IndexRequest(BaseModel):
    """POST /index body."""

    url: str


class SearchRequest(BaseModel):
    """POST /api/search body."""

    query: str
    mode: str | None = Field(default="general", description="general | academic | code | writing")
    limit: int = Field(default=10, ge=1, le=50)
    stream: bool = Field(default=False, description="Stream results as they're reranked")
    filters: dict | None = Field(default=None, description="Optional filters e.g. domain, freshness")


class SourceResponse(BaseModel):
    """Single source in search response."""

    id: str
    url: str
    title: str
    snippet: str
    score: float
    domain: str | None = None


class AnswerRequest(BaseModel):
    """POST /api/answer body."""

    query: str
    mode: str | None = Field(default="general", description="general | academic | code | writing")
    limit: int = Field(default=10, ge=1, le=30, description="Number of text sources")
    session_id: str | None = Field(default=None, description="Session ID for follow-up context")
    history: list[dict] | None = Field(default=None, description="Previous Q&A for session context")
    include_images: bool = Field(default=True, description="Whether to fetch image results")
