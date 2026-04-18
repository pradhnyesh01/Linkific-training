"""
01_sync_vs_async.py
Sync vs Async — Side-by-Side Comparison

Shows WHY async matters when making multiple I/O-bound calls.
No external server needed — this runs standalone.

Key insight:
  Sync  → tasks run one after another  (total = sum of all delays)
  Async → tasks run concurrently       (total ≈ max of all delays)
"""

import asyncio
import time
import httpx


# ── Simulated "slow" tasks ────────────────────────────────────────────────────

def slow_task_sync(name: str, delay: float) -> str:
    """A blocking (sync) task — holds up the whole thread while sleeping."""
    time.sleep(delay)
    return f"{name} done in {delay}s"


async def slow_task_async(name: str, delay: float) -> str:
    """A non-blocking (async) task — yields control while waiting."""
    await asyncio.sleep(delay)
    return f"{name} done in {delay}s"


# ── Sync approach ─────────────────────────────────────────────────────────────

def run_sync():
    """Runs 3 tasks sequentially. Total = sum of all delays."""
    print("\n--- SYNC (sequential) ---")
    tasks = [("TaskA", 1.0), ("TaskB", 0.8), ("TaskC", 0.6)]
    start = time.perf_counter()

    results = []
    for name, delay in tasks:
        result = slow_task_sync(name, delay)
        print(f"  {result}")
        results.append(result)

    elapsed = time.perf_counter() - start
    print(f"  Total time: {elapsed:.2f}s  (expected ≈ {sum(d for _, d in tasks):.1f}s)")
    return results


# ── Async approach ────────────────────────────────────────────────────────────

async def run_async():
    """Runs 3 tasks concurrently. Total ≈ max of delays."""
    print("\n--- ASYNC (concurrent) ---")
    tasks = [("TaskA", 1.0), ("TaskB", 0.8), ("TaskC", 0.6)]
    start = time.perf_counter()

    # asyncio.gather runs all coroutines concurrently
    results = await asyncio.gather(*[slow_task_async(n, d) for n, d in tasks])

    for r in results:
        print(f"  {r}")

    elapsed = time.perf_counter() - start
    print(f"  Total time: {elapsed:.2f}s  (expected ≈ {max(d for _, d in tasks):.1f}s)")
    return results


# ── Async HTTP requests (real-world example) ──────────────────────────────────

async def fetch_url(client: httpx.AsyncClient, url: str) -> dict:
    """Fetch a single URL asynchronously."""
    start = time.perf_counter()
    try:
        resp = await client.get(url, timeout=10.0)
        elapsed = time.perf_counter() - start
        return {"url": url, "status": resp.status_code, "time_s": round(elapsed, 3)}
    except Exception as e:
        return {"url": url, "error": str(e)}


async def run_async_http():
    """
    Fetch multiple URLs concurrently using httpx.AsyncClient.
    Compare with fetching them one by one.
    """
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    print("\n--- ASYNC HTTP: 3 URLs fetched concurrently ---")
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[fetch_url(client, u) for u in urls])
    elapsed = time.perf_counter() - start

    for r in results:
        print(f"  {r}")
    print(f"  Concurrent total: {elapsed:.2f}s")

    print("\n--- SYNC HTTP: 3 URLs fetched sequentially ---")
    start = time.perf_counter()
    sync_results = []
    with httpx.Client() as client:
        for url in urls:
            t = time.perf_counter()
            try:
                resp = client.get(url, timeout=10.0)
                sync_results.append({"url": url, "status": resp.status_code,
                                     "time_s": round(time.perf_counter()-t, 3)})
            except Exception as e:
                sync_results.append({"url": url, "error": str(e)})
    elapsed = time.perf_counter() - start
    for r in sync_results:
        print(f"  {r}")
    print(f"  Sequential total: {elapsed:.2f}s")



async def explain_async():
    """Walk through the key async concepts with commentary."""
    print("\n--- ASYNC CONCEPTS ---")

    # 1. await pauses the coroutine and lets other tasks run
    print("\n1. await asyncio.sleep() — yields control")
    await asyncio.sleep(0)
    print("   (control was yielded and returned)")

    # 2. asyncio.gather — run multiple coroutines at once
    print("\n2. asyncio.gather — concurrent execution")
    results = await asyncio.gather(
        slow_task_async("X", 0.2),
        slow_task_async("Y", 0.2),
        slow_task_async("Z", 0.2),
    )
    print(f"   Results: {results}")

    # 3. asyncio.wait_for — add a timeout
    print("\n3. asyncio.wait_for — timeout after N seconds")
    try:
        result = await asyncio.wait_for(slow_task_async("Slow", 5.0), timeout=0.5)
    except asyncio.TimeoutError:
        print("   TimeoutError raised after 0.5s (task would have taken 5s)")

    # 4. Tasks — fire and forget
    print("\n4. asyncio.create_task — start a task without waiting")
    task = asyncio.create_task(slow_task_async("Background", 0.1))
    print("   Task created — doing other work...")
    await asyncio.sleep(0.05)
    print("   ...still doing work...")
    result = await task   # now wait for it
    print(f"   Task finished: {result}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Sync vs Async Performance Comparison")
    print("=" * 55)

    # 1. Simulated tasks
    run_sync()
    asyncio.run(run_async())

    print("\n" + "="*55)
    print("  Speedup = sync_time / async_time")
    print("  With 3 tasks of 1.0 + 0.8 + 0.6 = 2.4s total:")
    print("  Sync ≈ 2.4s | Async ≈ 1.0s | ~2.4x faster")
    print("="*55)

    # 2. Async concepts walkthrough
    asyncio.run(explain_async())

    # 3. Real HTTP
    asyncio.run(run_async_http())
    print("\n  (Uncomment run_async_http() to test with real HTTP calls)")
