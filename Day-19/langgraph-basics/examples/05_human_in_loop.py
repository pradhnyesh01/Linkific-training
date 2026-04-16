"""
Example 5 – Human-in-the-Loop with Checkpointing
Flow: write_draft → [PAUSE for human] → approved? → send   → END
                                                  → revise → [PAUSE for human] (loops)

MemorySaver  : saves state after every node so execution can be resumed.
interrupt_before: pauses the graph BEFORE that node runs — human can update state first.
thread_id    : unique ID for each conversation session (like a session ID).
"""

import os
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── State ─────────────────────────────────────────────────────────────────────
class State(TypedDict):
    topic:    str
    draft:    str
    approved: bool
    feedback: str
    status:   str


# ── Nodes ─────────────────────────────────────────────────────────────────────
def write_draft(state: State) -> State:
    resp = llm.invoke(f"Write a 3-sentence professional email about: {state['topic']}")
    print(f"  [write_draft] draft ready")
    return {"draft": resp.content}


def human_review(state: State) -> State:
    # This node body does nothing — execution is paused BEFORE it runs.
    # The human updates state externally, then resumes.
    print("  [human_review] graph paused — waiting for human decision")
    return {}


def send_email(state: State) -> State:
    print("  [send_email] email sent!")
    return {"status": "Email approved and sent."}


def revise_draft(state: State) -> State:
    print(f"  [revise_draft] revising with feedback: '{state['feedback']}'")
    prompt = (
        f"Revise this email based on feedback.\n\n"
        f"Email:\n{state['draft']}\n\n"
        f"Feedback: {state['feedback']}"
    )
    resp = llm.invoke(prompt)
    return {"draft": resp.content, "feedback": "", "approved": False}


# ── Conditional edge ──────────────────────────────────────────────────────────
def route_review(state: State) -> str:
    return "approved" if state["approved"] else "revise"


# ── Build graph ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("write_draft",  write_draft)
builder.add_node("human_review", human_review)
builder.add_node("send_email",   send_email)
builder.add_node("revise_draft", revise_draft)

builder.set_entry_point("write_draft")
builder.add_edge("write_draft",  "human_review")
builder.add_conditional_edges(
    "human_review", route_review,
    {"approved": "send_email", "revise": "revise_draft"}
)
builder.add_edge("send_email",   END)
builder.add_edge("revise_draft", "human_review")   # loop back for re-review

# Compile with checkpointing + interrupt
memory = MemorySaver()
app    = builder.compile(checkpointer=memory, interrupt_before=["human_review"])


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Human-in-the-Loop Graph ===\n")

    png_path = "../graphs/05_human_in_loop.png"
    with open(png_path, "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print(f"Graph saved → {png_path}\n")

    # ── Scenario A: human approves on first try ──
    print("\n--- Scenario A: Approve on first try ---")
    config_a = {"configurable": {"thread_id": "session-A"}}

    # Run until interrupt
    state = app.invoke(
        {"topic": "meeting reschedule", "draft": "", "approved": False, "feedback": "", "status": ""},
        config=config_a
    )
    print(f"\nDraft:\n{state['draft']}\n")

    # Human approves
    print("Human decision: APPROVED")
    app.update_state(config_a, {"approved": True}, as_node="human_review")
    final = app.invoke(None, config=config_a)
    print(f"Result: {final['status']}")

    # ── Scenario B: human rejects, then approves ──
    print("\n--- Scenario B: Reject then approve ---")
    config_b = {"configurable": {"thread_id": "session-B"}}

    state = app.invoke(
        {"topic": "project delay notification", "draft": "", "approved": False, "feedback": "", "status": ""},
        config=config_b
    )
    print(f"\nDraft:\n{state['draft']}\n")

    # Human rejects with feedback
    print("Human decision: REJECTED — 'Make it shorter and more direct.'")
    app.update_state(config_b, {"approved": False, "feedback": "Make it shorter and more direct."}, as_node="human_review")
    state2 = app.invoke(None, config=config_b)
    print(f"\nRevised draft:\n{state2['draft']}\n")

    # Human approves revision
    print("Human decision: APPROVED")
    app.update_state(config_b, {"approved": True}, as_node="human_review")
    final2 = app.invoke(None, config=config_b)
    print(f"Result: {final2['status']}")
