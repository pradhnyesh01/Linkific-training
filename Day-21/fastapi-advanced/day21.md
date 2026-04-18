# Day 21 – FastAPI Advanced

## Setup

```bash
cd Day-21/fastapi-advanced
pip install fastapi uvicorn httpx pydantic python-dotenv
uvicorn main:app --reload
```

Interactive docs: **http://127.0.0.1:8000/docs**

---

## Features

### 1. Async Endpoints
Every endpoint uses `async def`. FastAPI can handle other requests while one is waiting for I/O.

```python
@app.get("/async-demo")
async def async_demo():
    # 3 calls run concurrently — total ≈ 0.5s, not 1.2s
    results = await asyncio.gather(
        fetch("ServiceA", 0.5),
        fetch("ServiceB", 0.3),
        fetch("ServiceC", 0.4),
    )
```

### 2. Dependency Injection
Dependencies are functions FastAPI calls before your endpoint runs.

```python
# Reusable across any endpoint
async def verify_api_key(x_api_key: str = Header(None)) -> str:
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(403, "Invalid API key")
    return x_api_key

@app.post("/items")
async def create_item(api_key: str = Depends(verify_api_key)):
    ...
```

**Dependencies used:**
| Dependency | What it does |
|---|---|
| `verify_api_key` | Checks X-API-Key header, raises 401/403 if missing/wrong |
| `optional_api_key` | Returns key if valid, None if not — never raises |
| `get_pagination` | Parses `page` and `per_page` query params |
| `get_category_filter` | Validates `category` query param against allowed list |

### 3. Middleware
Middleware runs for every request and response.

```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start    = time.perf_counter()
        response = await call_next(request)           # call the endpoint
        elapsed  = (time.perf_counter() - start) * 1000
        logger.info(f"{request.method}  {request.url.path}  {response.status_code}  {elapsed:.1f}ms")
        response.headers["X-Process-Time"] = f"{elapsed:.2f}ms"
        return response
```

Every response has an `X-Process-Time` header showing how long it took.

### 4. API Versioning
v1 and v2 run side by side via `APIRouter`:

```python
v1 = APIRouter(prefix="/v1", tags=["v1"])
v2 = APIRouter(prefix="/v2", tags=["v2"])

@v1.get("/items")   # GET /v1/items  — price in rupees
@v2.get("/items")   # GET /v2/items  — price in paise (breaking change)
```

### 5. Background Tasks
Response is returned to the client immediately; slow work happens after.

```python
@app.post("/send-email")
async def send_email(payload: EmailRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_background, payload.to, payload.subject)
    return {"message": "Email queued"}   # ← client gets this instantly
    # send_email_background runs after response is sent
```

### 6. Pydantic Validation
FastAPI validates all request bodies automatically using Pydantic models.

```python
class ItemCreate(BaseModel):
    name:     str   = Field(..., min_length=1, max_length=100)
    price:    float = Field(..., gt=0)           # must be > 0
    category: str                                 # validated by @field_validator
```

If invalid data is sent → automatic 422 Unprocessable Entity with detailed error.

### 7. Error Handling

Custom exception handlers return consistent JSON:
```json
{"detail": "Route '/xyz' not found.", "error_code": "NOT_FOUND"}
```

### 8. CORS
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

---

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| GET | `/v1/items` | No | List items (filter + paginate) |
| GET | `/v1/items/{id}` | No | Get one item |
| POST | `/v1/items` | Yes | Create item + background log |
| PUT | `/v1/items/{id}` | Yes | Update item |
| DELETE | `/v1/items/{id}` | Yes | Delete item |
| GET | `/v1/users` | Yes | List users |
| POST | `/v1/users` | Yes | Create user |
| POST | `/v1/send-email` | Yes | Queue email (background task) |
| GET | `/v1/email-log` | Yes | View sent emails |
| GET | `/v1/async-demo` | No | Concurrent sub-calls demo |
| GET | `/v2/items` | No | Items with price in paise (v2) |
| GET | `/v2/items/{id}` | No | Item with paise + api_version |

**Authentication:** Add header `X-API-Key: dev-key-123`

---

## Running Examples

```bash
# Terminal 1 — start server
uvicorn main:app --reload

# Terminal 2 — run examples
python examples/01_sync_vs_async.py    # no server needed
python examples/02_background_tasks.py
python examples/03_performance_test.py
```

---

## Sync vs Async — Quick Summary

| | Sync | Async |
|---|---|---|
| **Runs when** | Tasks are sequential | Tasks involve I/O (HTTP, DB) |
| **Total time** | Sum of all delays | Max of all delays |
| **Use for** | Simple scripts | APIs, concurrent requests |
| **Keyword** | `def`, `time.sleep` | `async def`, `await asyncio.sleep` |

---

## Performance Results (10 requests)

| Endpoint | Sync total | Async total | Speedup |
|---|---|---|---|
| `/health` | ~2.0s | ~0.3s | ~7x |
| `/v1/items` | ~2.0s | ~0.3s | ~7x |
| `/v1/async-demo` | ~5.0s | ~0.6s | ~8x |

*(Actual numbers vary by machine and network.)*
