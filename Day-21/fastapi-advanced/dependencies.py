"""
dependencies.py
Dependency Injection examples for FastAPI.

Dependencies are functions that FastAPI calls automatically before your
endpoint runs. They can:
  - Validate headers / tokens
  - Parse common query parameters
  - Open/close DB connections
  - Log requests

Usage in endpoints:
    @router.get("/items")
    async def list_items(
        pagination: Pagination = Depends(get_pagination),
        api_key:    str        = Depends(verify_api_key),
    ):
        ...
"""

from fastapi import Depends, Header, HTTPException, Query, status
from typing import Optional


# ── Fake valid API keys (in production, check a database) ─────────────────────

VALID_API_KEYS = {"dev-key-123", "prod-key-456", "test-key-789"}


# ── Dependency 1: API key authentication ──────────────────────────────────────

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Reads X-API-Key header. Raises 401 if missing or invalid.
    Inject into any endpoint that needs authentication.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return x_api_key


# ── Dependency 2: Pagination parameters ───────────────────────────────────────

class Pagination:
    """Reusable pagination parameters."""
    def __init__(
        self,
        page:     int = Query(1,   ge=1,          description="Page number (1-based)"),
        per_page: int = Query(10,  ge=1, le=100,  description="Items per page (max 100)"),
    ):
        self.page     = page
        self.per_page = per_page
        self.offset   = (page - 1) * per_page

    def paginate(self, items: list) -> dict:
        """Slice a list and return pagination metadata."""
        total = len(items)
        pages = (total + self.per_page - 1) // self.per_page
        sliced = items[self.offset: self.offset + self.per_page]
        return {
            "items":    sliced,
            "total":    total,
            "page":     self.page,
            "per_page": self.per_page,
            "pages":    pages,
        }


def get_pagination(
    page:     int = Query(1,  ge=1),
    per_page: int = Query(10, ge=1, le=100),
) -> Pagination:
    return Pagination(page=page, per_page=per_page)


# ── Dependency 3: Optional auth (public endpoints that benefit from user info) ─

async def optional_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Returns the API key if valid, or None if not provided. Never raises."""
    if x_api_key and x_api_key in VALID_API_KEYS:
        return x_api_key
    return None


# ── Dependency 4: Category filter ─────────────────────────────────────────────

def get_category_filter(
    category: Optional[str] = Query(None, description="Filter by category"),
) -> Optional[str]:
    """Validates and returns an optional category filter."""
    allowed = {"electronics", "food", "clothing", "other"}
    if category and category.lower() not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{category}'. Allowed: {sorted(allowed)}",
        )
    return category.lower() if category else None
