"""
Example 3 – Loop (Retry Until Success)
Flow: START → worker → check → success? → END
                             → retry?   → worker  (loops back)
                             → failed?  → on_failure → END

Conditional edges can point back to earlier nodes, creating a loop.
Always add a max_attempts guard to prevent infinite loops.
"""

import os
import random
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END

load_dotenv(find_dotenv())


# ── State ─────────────────────────────────────────────────────────────────────
class State(TypedDict):
    task:     str
    attempts: int
    success:  bool
    result:   str


# ── Nodes ─────────────────────────────────────────────────────────────────────
def worker(state: State) -> State:
    """Simulate a task that randomly succeeds or fails."""
    attempt = state["attempts"] + 1
    success = random.random() > 0.5   # 50% chance each try
    print(f"  [worker] attempt {attempt} → {'SUCCESS' if success else 'FAILED'}")
    return {
        "attempts": attempt,
        "success":  success,
        "result":   f"Completed on attempt {attempt}." if success else ""
    }


def on_failure(state: State) -> State:
    """Called when max attempts are exhausted."""
    print("  [on_failure] giving up after max attempts")
    return {"result": f"Task failed after {state['attempts']} attempts."}


# ── Conditional edge ──────────────────────────────────────────────────────────
MAX_ATTEMPTS = 4

def should_retry(state: State) -> str:
    if state["success"]:
        return "done"
    if state["attempts"] >= MAX_ATTEMPTS:
        return "failed"
    return "retry"


# ── Build graph ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("worker",     worker)
builder.add_node("on_failure", on_failure)

builder.set_entry_point("worker")
builder.add_conditional_edges(
    "worker",
    should_retry,
    {
        "done":   END,           # success → stop
        "retry":  "worker",      # fail    → loop back to worker
        "failed": "on_failure",  # too many → failure node
    }
)
builder.add_edge("on_failure", END)

app = builder.compile()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Loop / Retry Graph ===\n")

    png_path = "../graphs/03_loop.png"
    with open(png_path, "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print(f"Graph saved → {png_path}\n")

    random.seed(99)
    print("\nRunning task with retry logic:")
    result = app.invoke({"task": "process_data", "attempts": 0, "success": False, "result": ""})
    print(f"\nFinal: {result['result']}")
