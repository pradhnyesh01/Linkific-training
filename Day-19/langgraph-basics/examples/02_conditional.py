"""
Example 2 – Conditional Routing
Flow: classify → (positive?) → positive_handler → END
                             → negative_handler → END

A conditional edge function returns a string (next node name).
The graph branches based on what the function returns.
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
    text:      str
    sentiment: str
    response:  str


# ── Nodes ─────────────────────────────────────────────────────────────────────
def classify(state: State) -> State:
    prompt   = f"Classify as 'positive' or 'negative'. One word only.\n{state['text']}"
    result   = llm.invoke(prompt).content.strip().lower()
    print(f"  [classify] → {result}")
    return {"sentiment": result}


def handle_positive(state: State) -> State:
    print("  [handle_positive]")
    return {"response": "Thank you for your positive feedback! We're glad you're happy."}


def handle_negative(state: State) -> State:
    print("  [handle_negative]")
    return {"response": "We're sorry to hear that. Our support team will contact you shortly."}


# ── Conditional edge function ─────────────────────────────────────────────────
def route_by_sentiment(state: State) -> str:
    """Return the name of the next node based on sentiment."""
    return "positive" if "positive" in state["sentiment"] else "negative"


# ── Build graph ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("classify",  classify)
builder.add_node("positive",  handle_positive)
builder.add_node("negative",  handle_negative)

builder.set_entry_point("classify")

# add_conditional_edges(from_node, router_fn, {return_value: next_node})
builder.add_conditional_edges(
    "classify",
    route_by_sentiment,
    {
        "positive": "positive",
        "negative": "negative",
    }
)

builder.add_edge("positive", END)
builder.add_edge("negative", END)

app = builder.compile()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Conditional Routing Graph ===\n")

    png_path = "../graphs/02_conditional.png"
    with open(png_path, "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())
    print(f"Graph saved → {png_path}\n")

    reviews = [
        "This product is absolutely amazing, I love it!",
        "The worst experience I have ever had. Very disappointed.",
    ]

    for text in reviews:
        print(f"\nInput: {text}")
        result = app.invoke({"text": text, "sentiment": "", "response": ""})
        print(f"Response: {result['response']}")
