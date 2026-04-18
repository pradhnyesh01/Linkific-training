"""
03_performance_test.py
Performance Comparison — Sync vs Async requests

Compares making N requests to the FastAPI server:
  - Sequentially (sync) with httpx.Client
  - Concurrently (async) with httpx.AsyncClient + asyncio.gather

Shows the real-world benefit of async I/O.

Requires: uvicorn main:app --reload  (in another terminal)
Install:  pip install httpx
"""

import asyncio
import time
import httpx
from statistics import mean, stdev


BASE_URL = "http://127.0.0.1:8000"
API_KEY  = "dev-key-123"
HEADERS  = {"X-API-Key": API_KEY}


# ── Single request helpers ────────────────────────────────────────────────────

def sync_request(client: httpx.Client, url: str) -> float:
    """Make one sync GET request. Returns time taken in seconds."""
    start = time.perf_counter()
    client.get(url, headers=HEADERS, timeout=10.0)
    return time.perf_counter() - start


async def async_request(client: httpx.AsyncClient, url: str) -> float:
    """Make one async GET request. Returns time taken in seconds."""
    start = time.perf_counter()
    await client.get(url, headers=HEADERS, timeout=10.0)
    return time.perf_counter() - start


# ── Benchmark: Sequential ─────────────────────────────────────────────────────

def benchmark_sync(url: str, n: int) -> dict:
    """
    Make N requests one after another (blocking).
    Total time = sum of each request's time.
    """
    times = []
    with httpx.Client() as client:
        for _ in range(n):
            t = sync_request(client, url)
            times.append(t)

    return {
        "mode":    "sync (sequential)",
        "n":       n,
        "total_s": round(sum(times), 3),
        "mean_ms": round(mean(times) * 1000, 1),
        "min_ms":  round(min(times) * 1000, 1),
        "max_ms":  round(max(times) * 1000, 1),
    }


# ── Benchmark: Concurrent ─────────────────────────────────────────────────────

async def benchmark_async(url: str, n: int) -> dict:
    """
    Make N requests concurrently (non-blocking).
    Total time ≈ time of the slowest single request.
    """
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        times = await asyncio.gather(*[async_request(client, url) for _ in range(n)])
        total = time.perf_counter() - start

    return {
        "mode":    "async (concurrent)",
        "n":       n,
        "total_s": round(total, 3),
        "mean_ms": round(mean(times) * 1000, 1),
        "min_ms":  round(min(times) * 1000, 1),
        "max_ms":  round(max(times) * 1000, 1),
    }


# ── Print result ──────────────────────────────────────────────────────────────

def print_result(result: dict):
    print(f"\n  Mode    : {result['mode']}")
    print(f"  Requests: {result['n']}")
    print(f"  Total   : {result['total_s']}s")
    print(f"  Per-req : mean={result['mean_ms']}ms  min={result['min_ms']}ms  max={result['max_ms']}ms")


# ── Main benchmark ────────────────────────────────────────────────────────────

async def run_benchmark():
    # Test endpoints
    endpoints = [
        ("/health",         "Health check (no DB/auth)"),
        ("/v1/items",       "List items (pagination + filter)"),
        ("/v1/async-demo",  "Async demo (3 concurrent sub-calls)"),
    ]

    N = 10   # requests per test (keep low to be polite to the server)

    print(f"\n{'='*58}")
    print(f"  Performance Test — {N} requests per endpoint")
    print(f"{'='*58}")

    for path, label in endpoints:
        url = BASE_URL + path
        print(f"\n  Endpoint: {label}")
        print(f"  URL     : {url}")

        # Sync
        sync_result  = benchmark_sync(url, N)
        # Async
        async_result = await benchmark_async(url, N)

        print_result(sync_result)
        print_result(async_result)

        speedup = sync_result["total_s"] / max(async_result["total_s"], 0.001)
        print(f"\n  ⚡ Speedup: {speedup:.1f}x  (async vs sync)")

    print(f"\n{'='*58}")
    print("  Summary")
    print(f"{'='*58}")
    print("""
  Sync  → each request blocks the thread until it completes.
           Total time = sum of all response times.

  Async → all requests are sent at once; we await results together.
           Total time ≈ the slowest single response.

  The async speedup grows with N (more requests = bigger difference).
  For CPU-bound tasks (pure computation), async gives no benefit.
  For I/O-bound tasks (HTTP, DB, file reads), async is much faster.
    """)


# ── Endpoint-level feature tests ──────────────────────────────────────────────

async def test_features():
    """Quick smoke test for all major API features."""
    print(f"\n{'='*58}")
    print("  Feature Smoke Tests")
    print(f"{'='*58}")

    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # 1. Health check
        r = await client.get("/health")
        print(f"\n  [{'✓' if r.status_code==200 else '✗'}] GET /health  → {r.status_code}")

        # 2. List items (public)
        r = await client.get("/v1/items?page=1&per_page=3")
        data = r.json()
        print(f"  [{'✓' if r.status_code==200 else '✗'}] GET /v1/items  → {data.get('total')} total, {len(data.get('items',[]))} returned")

        # 3. Category filter
        r = await client.get("/v1/items?category=electronics")
        print(f"  [{'✓' if r.status_code==200 else '✗'}] GET /v1/items?category=electronics  → {r.json().get('total')} items")

        # 4. Auth required — no key
        r = await client.post("/v1/items", json={"name":"x","price":10,"category":"other"})
        print(f"  [{'✓' if r.status_code==401 else '✗'}] POST /v1/items (no key)  → {r.status_code} (expected 401)")

        # 5. Auth required — valid key
        r = await client.post("/v1/items",
            json={"name":"Test Item","price":99.0,"category":"other","in_stock":True},
            headers=HEADERS)
        print(f"  [{'✓' if r.status_code==201 else '✗'}] POST /v1/items (with key)  → {r.status_code} id={r.json().get('id')}")

        # 6. Invalid category
        r = await client.get("/v1/items?category=invalid_cat")
        print(f"  [{'✓' if r.status_code==400 else '✗'}] GET /v1/items?category=invalid  → {r.status_code} (expected 400)")

        # 7. 404 for unknown item
        r = await client.get("/v1/items/9999")
        print(f"  [{'✓' if r.status_code==404 else '✗'}] GET /v1/items/9999  → {r.status_code} (expected 404)")

        # 8. v2 endpoint
        r = await client.get("/v2/items/1")
        data = r.json()
        print(f"  [{'✓' if r.status_code==200 else '✗'}] GET /v2/items/1  → price_paise={data.get('price_paise')} (v2 format)")

        # 9. Async demo
        r = await client.get("/v1/async-demo")
        data = r.json()
        print(f"  [{'✓' if r.status_code==200 else '✗'}] GET /v1/async-demo  → total_time={data.get('total_time_s')}s")

        # 10. Check X-Process-Time header (from middleware)
        r = await client.get("/health")
        proc_time = r.headers.get("x-process-time", "missing")
        print(f"  [{'✓' if proc_time != 'missing' else '✗'}] X-Process-Time header  → {proc_time}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Requires server: uvicorn main:app --reload")
    print("Running from Day-21/fastapi-advanced/\n")

    try:
        # Quick connectivity check
        with httpx.Client() as c:
            c.get(f"{BASE_URL}/health", timeout=2.0)

        asyncio.run(test_features())
        asyncio.run(run_benchmark())

    except httpx.ConnectError:
        print("✗ Cannot connect to server.")
        print("  Start it first: uvicorn main:app --reload")
        print("  Then re-run this script.")
