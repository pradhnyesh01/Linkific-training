"""
middleware.py
Custom middleware for the FastAPI app.

Middleware runs for EVERY request/response — before the endpoint
and after the response is prepared.

Included here:
  1. RequestLoggingMiddleware  — logs method, path, status, and time taken
  2. add_cors_middleware()     — configures CORS headers
  3. add_error_handlers()      — custom JSON error pages for 404/500
"""

import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# ── Logger setup ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fastapi-advanced")


# ── Middleware 1: Request logging + timing ────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request with:
      METHOD  /path  →  STATUS  (Xms)

    Attaches X-Process-Time header to every response.
    """

    async def dispatch(self, request: Request, call_next):
        start     = time.perf_counter()
        response  = await call_next(request)
        elapsed   = (time.perf_counter() - start) * 1000  # ms

        logger.info(
            f"{request.method:6s}  {request.url.path:<40s}  "
            f"→  {response.status_code}  ({elapsed:.1f}ms)"
        )
        response.headers["X-Process-Time"] = f"{elapsed:.2f}ms"
        return response


# ── CORS setup ────────────────────────────────────────────────────────────────

def add_cors_middleware(app: FastAPI):
    """
    Allow cross-origin requests.
    In production, replace allow_origins=["*"] with your actual frontend domain.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # open for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ── Custom error handlers ─────────────────────────────────────────────────────

def add_error_handlers(app: FastAPI):
    """Register custom JSON responses for common HTTP errors."""

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail":     f"Route '{request.url.path}' not found.",
                "error_code": "NOT_FOUND",
            },
        )

    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        logger.error(f"Unhandled error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail":     "An internal server error occurred.",
                "error_code": "INTERNAL_ERROR",
            },
        )
