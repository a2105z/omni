"""
Omni API Gateway - FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.core.config import settings
from app.core.rate_limit import check_rate_limit


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    yield
    # Cleanup (e.g., close connections) can go here


app = FastAPI(
    title="Omni API",
    description="Perplexity-style search engine backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Step 20: Rate limiting by client IP."""
    if request.url.path.startswith("/api/answer") or request.url.path.startswith("/api/search"):
        client = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("x-forwarded-for")
        key = (forwarded or client).split(",")[0].strip()
        if not check_rate_limit(key, settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status_code=429,
            )
    return await call_next(request)


app.include_router(routes.router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Health check root."""
    return {"service": "omni", "status": "ok"}
