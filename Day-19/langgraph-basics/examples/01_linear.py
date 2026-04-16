"""
Example 1 – Simple Linear Graph
Flow: START → clean_text → summarise → END
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
    text:   str
    result: str


# ── Nodes ─────────────────────────────────────────────────────────────────────
def clean_text(state: State) -> State:
    """Node 1: strip whitespace and lowercase."""
    cleaned = state["text"].strip().lower()
    print(f"  [clean_text] '{state['text']}' → '{cleaned}'")
    return {"text": cleaned}


def summarise(state: State) -> State:
    """Node 2: ask LLM for a one-sentence summary."""
    response = llm.invoke(f"Summarise in one sentence: {state['text']}")
    print(f"  [summarise] done")
    return {"result": response.content}


# ── Build graph ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("clean",     clean_text)
builder.add_node("summarise", summarise)

builder.set_entry_point("clean")
builder.add_edge("clean",     "summarise")
builder.add_edge("summarise", END)

app = builder.compile()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Linear Graph ===\n")

    # Save graph as PNG
    png_path = "../graphs/01_linear.png"
    with open(png_path, "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print(f"Graph saved → {png_path}\n")

    result = app.invoke({
        "text":   "  Machine learning is a subset of artificial intelligence.  ",
        "result": ""
    })

    print(f"\nFinal result: {result['result']}")
