"""Centralized error handling."""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class OmniError(Exception):
    """Base exception for Omni backend."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class CrawlerError(OmniError):
    """Crawler-related errors."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code)


class ParserError(OmniError):
    """Parser-related errors."""

    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message, status_code)


class IndexerError(OmniError):
    """Indexer-related errors."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message, status_code)


class VectorStoreError(OmniError):
    """Vector store-related errors."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message, status_code)


async def omni_exception_handler(request: Request, exc: OmniError) -> JSONResponse:
    """Handle OmniError with proper HTTP response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": str(exc)},
    )
