"""
02_background_tasks.py
Background Tasks — How They Work

FastAPI's BackgroundTasks run AFTER the response is sent.
The client gets the response immediately; the slow work happens behind the scenes.

Flow:
  Client → POST /send-email
  Server → returns {"message": "Email queued"} immediately  ← client sees this
  Server → [runs send_email_background in background]        ← client doesn't wait

This file shows:
  1. How to call the background task endpoint
  2. How to use BackgroundTasks in a simple script (no server)
  3. Multiple background tasks in one request
"""

import asyncio
import time
import httpx


BASE_URL  = "http://127.0.0.1:8000"
API_KEY   = "dev-key-123"
HEADERS   = {"X-API-Key": API_KEY}


# ── Part 1: Standalone background task demo (no server needed) ─────────────────

def simulate_background_task(task_name: str, delay: float, result_store: list):
    """Simulates a slow background job."""
    print(f"  [BG] {task_name} started...")
    time.sleep(delay)
    result_store.append({"task": task_name, "completed_at": time.time()})
    print(f"  [BG] {task_name} done after {delay}s")


async def demo_background_concept():
    """
    Show the core concept: response first, task later.
    Uses asyncio tasks to simulate FastAPI's BackgroundTasks.
    """
    print("\n--- Background Task Concept ---")

    results = []

    async def slow_job(name: str, delay: float):
        await asyncio.sleep(delay)
        results.append(name)
        print(f"  [BG DONE] {name}")

    # Simulate: request comes in → response sent → background job runs
    start = time.perf_counter()

    # Create background task (doesn't block)
    task = asyncio.create_task(slow_job("SendEmail", 1.5))

    # Response is returned immediately
    print(f"  Response sent to client after {time.perf_counter()-start:.3f}s")
    print("  Client is happy — doesn't wait for the background job")

    # Background continues after response
    await task
    print(f"  Background job finished at {time.perf_counter()-start:.2f}s total")


# ── Part 2: Call the actual FastAPI server ─────────────────────────────────────

async def demo_api_background_task():
    """
    Send a request to POST /v1/send-email.
    The server responds instantly; email is sent in background.
    """
    print("\n--- API: Background Email Task ---")
    print("  (Make sure the server is running: uvicorn main:app --reload)\n")

    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        try:
            resp = await client.post(
                f"{BASE_URL}/v1/send-email",
                json={
                    "to":      "user@example.com",
                    "subject": "Order Confirmed",
                    "body":    "Your order #1234 has been confirmed. Thank you!",
                },
                headers=HEADERS,
                timeout=5.0,
            )
            elapsed = time.perf_counter() - start
            print(f"  Response received in {elapsed:.3f}s:")
            print(f"  Status : {resp.status_code}")
            print(f"  Body   : {resp.json()}")
            print(f"\n  Notice: response came back in ~{elapsed:.2f}s")
            print(f"  The email is sending in the background right now...")
            print(f"  Check server terminal for '[BG TASK] Email sent to...'")

        except httpx.ConnectError:
            print("  Server not running. Start it with: uvicorn main:app --reload")


async def demo_multiple_background_tasks():
    """
    Create an item → background task logs it.
    Then send an email → background task sends it.
    Both background tasks run concurrently on the server.
    """
    print("\n--- Multiple Background Tasks in Sequence ---")

    async with httpx.AsyncClient() as client:
        # Task 1: Create item (triggers log background task)
        try:
            resp = await client.post(
                f"{BASE_URL}/v1/items",
                json={
                    "name":        "Test Headphones",
                    "description": "Created via background task demo",
                    "price":       1999.0,
                    "category":    "electronics",
                    "in_stock":    True,
                },
                headers=HEADERS,
                timeout=5.0,
            )
            print(f"  Create item → {resp.status_code}: {resp.json().get('name')}")

            # Task 2: Send email (triggers send background task)
            resp2 = await client.post(
                f"{BASE_URL}/v1/send-email",
                json={"to": "admin@shop.com", "subject": "New Item Added", "body": "Item created"},
                headers=HEADERS,
                timeout=5.0,
            )
            print(f"  Send email → {resp2.status_code}: {resp2.json().get('message')}")

            print("\n  Both requests returned instantly.")
            print("  Background tasks (log + email) are running on the server now.")

        except httpx.ConnectError:
            print("  Server not running. Start it with: uvicorn main:app --reload")


# ── Part 3: View the email log ─────────────────────────────────────────────────

async def view_email_log():
    """Check what emails were sent in the background."""
    print("\n--- Email Log (sent in background) ---")
    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(3)   # wait for background tasks to finish
            resp = await client.get(f"{BASE_URL}/v1/email-log", headers=HEADERS)
            data = resp.json()
            print(f"  Total emails sent: {data['count']}")
            for email in data["emails"]:
                print(f"  → to={email['to']}  subject={email['subject'][:30]}")
        except httpx.ConnectError:
            print("  Server not running.")



if __name__ == "__main__":
    print("=" * 55)
    print("  Background Tasks Demo")
    print("=" * 55)

    # Part 1: concept demo (no server needed)
    asyncio.run(demo_background_concept())

    # Parts 2 & 3: require the server running
    print("\n" + "="*55)
    print("  Parts below require: uvicorn main:app --reload")
    print("="*55)
    asyncio.run(demo_api_background_task())
    asyncio.run(demo_multiple_background_tasks())
    asyncio.run(view_email_log())
