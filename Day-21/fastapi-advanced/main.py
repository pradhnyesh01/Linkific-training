"""
main.py
FastAPI Advanced — Complete API

Features demonstrated:
  ✓ Async endpoints
  ✓ Dependency injection (API key auth, pagination, filters)
  ✓ Middleware (request logging, timing, CORS)
  ✓ Custom error handling
  ✓ API versioning (v1 and v2 routers)
  ✓ Background tasks
  ✓ Request validation with Pydantic

Run:
    cd Day-21/fastapi-advanced
    uvicorn main:app --reload

Docs: http://127.0.0.1:8000/docs
"""

import asyncio
import time
import json
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, APIRouter, status
from fastapi.responses import JSONResponse

from models import (
    ItemCreate, ItemResponse, ItemListResponse,
    UserCreate, UserResponse,
    EmailRequest, MessageResponse,
)
from dependencies import verify_api_key, get_pagination, get_category_filter, Pagination
from middleware import RequestLoggingMiddleware, add_cors_middleware, add_error_handlers


# ── In-memory "database" ──────────────────────────────────────────────────────

_items: list[dict] = [
    {"id": 1, "name": "Laptop",          "description": "14-inch ultrabook",   "price": 75000.0, "category": "electronics", "in_stock": True,  "created_at": datetime(2026, 3, 1)},
    {"id": 2, "name": "Rice (5kg)",       "description": "Basmati rice",        "price": 350.0,   "category": "food",        "in_stock": True,  "created_at": datetime(2026, 3, 5)},
    {"id": 3, "name": "T-Shirt",          "description": "Cotton round neck",   "price": 499.0,   "category": "clothing",    "in_stock": False, "created_at": datetime(2026, 3, 10)},
    {"id": 4, "name": "Wireless Mouse",   "description": "Bluetooth 5.0 mouse", "price": 1299.0,  "category": "electronics", "in_stock": True,  "created_at": datetime(2026, 3, 15)},
    {"id": 5, "name": "Running Shoes",    "description": "Size 42, blue",       "price": 2999.0,  "category": "clothing",    "in_stock": True,  "created_at": datetime(2026, 3, 20)},
]
_next_item_id = 6

_users: list[dict] = [
    {"id": 1, "username": "alice",   "email": "alice@example.com",   "age": 25},
    {"id": 2, "username": "bob",     "email": "bob@example.com",     "age": 30},
]
_next_user_id = 3

_email_log: list[dict] = []


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "FastAPI Advanced",
    description = "Day-21 — async endpoints, DI, middleware, versioning, background tasks",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# Add middleware and error handlers
app.add_middleware(RequestLoggingMiddleware)
add_cors_middleware(app)
add_error_handlers(app)


# ── Background task functions ─────────────────────────────────────────────────

def send_email_background(to: str, subject: str, body: str):
    """
    Simulated background email task.
    Runs AFTER the response is already sent to the client.
    """
    time.sleep(2)   # simulate slow email sending
    entry = {
        "to":        to,
        "subject":   subject,
        "body":      body[:50],
        "sent_at":   datetime.utcnow().isoformat(),
    }
    _email_log.append(entry)
    print(f"\n  [BG TASK] Email sent to {to} — subject: {subject}")


def log_item_creation(item_name: str, item_id: int):
    """Background task: log item creation to a file."""
    log_entry = {"event": "item_created", "name": item_name, "id": item_id,
                 "timestamp": datetime.utcnow().isoformat()}
    print(f"\n  [BG TASK] Item logged: {log_entry}")


# ── Health check (no auth) ────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Public health check — no authentication required."""
    return {
        "status":    "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version":   app.version,
    }


# ══════════════════════════════════════════════════════════════════════════════
# API v1 Router
# ══════════════════════════════════════════════════════════════════════════════

v1 = APIRouter(prefix="/v1", tags=["v1"])


# ── Items ─────────────────────────────────────────────────────────────────────

@v1.get("/items", response_model=ItemListResponse)
async def list_items_v1(
    pagination: Pagination       = Depends(get_pagination),
    category:   Optional[str]   = Depends(get_category_filter),
    in_stock:   Optional[bool]  = None,
):
    """
    List all items with optional filters and pagination.
    No authentication required.
    """
    filtered = _items[:]

    if category:
        filtered = [i for i in filtered if i["category"] == category]
    if in_stock is not None:
        filtered = [i for i in filtered if i["in_stock"] == in_stock]

    paged = pagination.paginate(filtered)
    return {**paged, "items": [ItemResponse(**i) for i in paged["items"]]}


@v1.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_v1(item_id: int):
    """Get a single item by ID."""
    item = next((i for i in _items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    return ItemResponse(**item)


@v1.post("/items", response_model=ItemResponse, status_code=201)
async def create_item_v1(
    payload:          ItemCreate,
    background_tasks: BackgroundTasks,
    api_key:          str = Depends(verify_api_key),
):
    """
    Create a new item. Requires X-API-Key header.
    Logs creation in the background.
    """
    global _next_item_id
    item = {
        "id":          _next_item_id,
        "name":        payload.name,
        "description": payload.description,
        "price":       payload.price,
        "category":    payload.category,
        "in_stock":    payload.in_stock,
        "created_at":  datetime.utcnow(),
    }
    _items.append(item)
    _next_item_id += 1

    background_tasks.add_task(log_item_creation, payload.name, item["id"])
    return ItemResponse(**item)


@v1.put("/items/{item_id}", response_model=ItemResponse)
async def update_item_v1(
    item_id: int,
    payload: ItemCreate,
    api_key: str = Depends(verify_api_key),
):
    """Update an existing item. Requires authentication."""
    item = next((i for i in _items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    item.update({
        "name":        payload.name,
        "description": payload.description,
        "price":       payload.price,
        "category":    payload.category,
        "in_stock":    payload.in_stock,
    })
    return ItemResponse(**item)


@v1.delete("/items/{item_id}", response_model=MessageResponse)
async def delete_item_v1(
    item_id: int,
    api_key: str = Depends(verify_api_key),
):
    """Delete an item. Requires authentication."""
    global _items
    item = next((i for i in _items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    _items = [i for i in _items if i["id"] != item_id]
    return {"message": f"Item {item_id} deleted.", "success": True}


# ── Users ──────────────────────────────────────────────────────────────────────

@v1.get("/users", response_model=list[UserResponse])
async def list_users_v1(api_key: str = Depends(verify_api_key)):
    """List all users. Requires authentication."""
    return [UserResponse(**u) for u in _users]


@v1.post("/users", response_model=UserResponse, status_code=201)
async def create_user_v1(
    payload: UserCreate,
    api_key: str = Depends(verify_api_key),
):
    """Create a new user."""
    global _next_user_id
    # Check for duplicate username
    if any(u["username"] == payload.username for u in _users):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' already exists.",
        )
    user = {"id": _next_user_id, **payload.model_dump()}
    _users.append(user)
    _next_user_id += 1
    return UserResponse(**user)


# ── Background task: Send email ───────────────────────────────────────────────

@v1.post("/send-email", response_model=MessageResponse)
async def send_email_v1(
    payload:          EmailRequest,
    background_tasks: BackgroundTasks,
    api_key:          str = Depends(verify_api_key),
):
    """
    Trigger an email send as a background task.
    The response is returned immediately — email is sent after.
    """
    background_tasks.add_task(
        send_email_background,
        payload.to,
        payload.subject,
        payload.body,
    )
    return {
        "message": f"Email queued for {payload.to}. Sending in background.",
        "success": True,
    }


@v1.get("/email-log", tags=["v1"])
async def get_email_log_v1(api_key: str = Depends(verify_api_key)):
    """View simulated sent emails."""
    return {"count": len(_email_log), "emails": _email_log}


# ── Async demo: concurrent fetch ──────────────────────────────────────────────

async def _fake_external_api(name: str, delay: float) -> dict:
    """Simulate calling an external API that takes `delay` seconds."""
    await asyncio.sleep(delay)
    return {"source": name, "data": f"result from {name}", "delay_s": delay}


@v1.get("/async-demo", tags=["v1"])
async def async_demo_v1():
    """
    Demonstrates async concurrency.
    Calls 3 'external APIs' concurrently with asyncio.gather().
    Total time ≈ max(delay) instead of sum(delays).
    """
    start = time.perf_counter()

    # These 3 calls run CONCURRENTLY, not sequentially
    results = await asyncio.gather(
        _fake_external_api("ServiceA", 0.5),
        _fake_external_api("ServiceB", 0.3),
        _fake_external_api("ServiceC", 0.4),
    )

    elapsed = time.perf_counter() - start
    return {
        "results":        results,
        "total_time_s":   round(elapsed, 3),
        "note":           "3 calls ran concurrently — total ≈ max(0.5, 0.3, 0.4) = 0.5s",
    }


# ══════════════════════════════════════════════════════════════════════════════
# API v2 Router  (breaking change: price is now an int in paise / cents)
# ══════════════════════════════════════════════════════════════════════════════

v2 = APIRouter(prefix="/v2", tags=["v2"])


@v2.get("/items", response_model=ItemListResponse)
async def list_items_v2(
    pagination: Pagination       = Depends(get_pagination),
    category:   Optional[str]   = Depends(get_category_filter),
):
    """
    v2 — Items list with price in paise (price * 100).
    Breaking change from v1: price is now an integer (paise).
    """
    filtered = _items[:]
    if category:
        filtered = [i for i in filtered if i["category"] == category]

    paged = pagination.paginate(filtered)
    # v2 change: convert price to paise
    v2_items = []
    for i in paged["items"]:
        v2_item = {**i, "price": int(i["price"] * 100)}
        v2_items.append(ItemResponse(**v2_item))

    return {**paged, "items": v2_items}


@v2.get("/items/{item_id}")
async def get_item_v2(item_id: int):
    """v2 — Single item with price in paise."""
    item = next((i for i in _items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")
    return {**ItemResponse(**item).model_dump(), "price_paise": int(item["price"] * 100),
            "api_version": "v2"}


# ── Mount routers ─────────────────────────────────────────────────────────────

app.include_router(v1)
app.include_router(v2)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
