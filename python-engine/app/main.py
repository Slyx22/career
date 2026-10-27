from __future__ import annotations

import os
import secrets

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router

app = FastAPI(
    title="Career Readiness Analyzer - Python Engine",
    description=(
        "CV parsing, evidence-aware skill extraction, explainable scoring, "
        "recommendations, and certificate generation for the Career "
        "Readiness Analyzer."
    ),
    version="0.1.0",
)

_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_ENGINE_API_KEY = os.environ.get("ENGINE_API_KEY", "")


@app.middleware("http")
async def require_engine_key(request: Request, call_next):
    """If ENGINE_API_KEY is set, only callers that send it (the website's
    server) may use /api/*. Off when unset, so local development and the
    current deployment keep working until the key is added on both sides."""
    if _ENGINE_API_KEY and request.url.path.startswith("/api/") and request.method != "OPTIONS":
        provided = request.headers.get("x-engine-key", "")
        if not secrets.compare_digest(provided, _ENGINE_API_KEY):
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces to clients (build spec section 31).
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong processing your request."},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(router, prefix="/api")
