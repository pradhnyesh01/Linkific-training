"""
Example 4 – Multi-Path Workflow
Flow: detect_type → code question    → code_handler    → format → END
                  → factual question → factual_handler → format → END
                  → other            → general_handler → format → END

Three different paths converge at the same format node.
"""

import os
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── State ─────────────────────────────────────────────────────────────────────
class State(TypedDict):
    question:   str
    q_type:     str
    raw_answer: str
    final:      str


# ── Nodes ─────────────────────────────────────────────────────────────────────
def detect_type(state: State) -> State:
    prompt = (
        "Classify this question as exactly one of: 'code', 'factual', or 'other'.\n"
        "Reply with one word only.\n"
        f"Question: {state['question']}"
    )
    q_type = llm.invoke(prompt).content.strip().lower()
    print(f"  [detect_type] → {q_type}")
    return {"q_type": q_type}


def code_handler(state: State) -> State:
    print("  [code_handler]")
    resp = llm.invoke(f"Give a short Python code example answering: {state['question']}")
    return {"raw_answer": resp.content}


def factual_handler(state: State) -> State:
    print("  [factual_handler]")
    resp = llm.invoke(f"Answer this factual question concisely: {state['question']}")
    return {"raw_answer": resp.content}


def general_handler(state: State) -> State:
    print("  [general_handler]")
    resp = llm.invoke(state["question"])
    return {"raw_answer": resp.content}


def format_output(state: State) -> State:
    label = f"[{state['q_type'].upper()}]"
    return {"final": f"{label} {state['raw_answer']}"}


# ── Conditional edge ──────────────────────────────────────────────────────────
def route_question(state: State) -> str:
    q = state["q_type"]
    if "code" in q:
        return "code"
    elif "factual" in q:
        return "factual"
    return "other"


# ── Build graph ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("detect",  detect_type)
builder.add_node("code",    code_handler)
builder.add_node("factual", factual_handler)
builder.add_node("other",   general_handler)
builder.add_node("format",  format_output)

builder.set_entry_point("detect")
builder.add_conditional_edges(
    "detect", route_question,
    {"code": "code", "factual": "factual", "other": "other"}
)

# All three paths converge at format
for node in ["code", "factual", "other"]:
    builder.add_edge(node, "format")
builder.add_edge("format", END)

app = builder.compile()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Multi-Path Workflow ===\n")

    png_path = "../graphs/04_multipath.png"
    with open(png_path, "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print(f"Graph saved → {png_path}\n")

    questions = [
        "How do I reverse a list in Python?",
        "What is the population of India?",
        "What should I have for lunch?",
    ]

    for q in questions:
        print(f"\nQuestion: {q}")
        result = app.invoke({"question": q, "q_type": "", "raw_answer": "", "final": ""})
        print(f"Answer: {result['final'][:150]}")
