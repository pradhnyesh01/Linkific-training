"""
Example 6 – State Management
Shows four important state patterns:
  A) Accumulating values (list append across nodes)
  B) Counters and numeric updates
  C) Partial updates (node only touches its own keys)
  D) State shared across a loop (value carries forward each iteration)
"""

import os
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import operator

load_dotenv(find_dotenv())
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ════════════════════════════════════════════════════════════════════════════════
# Pattern A – Accumulating list (each node appends to a shared list)
# ════════════════════════════════════════════════════════════════════════════════
# Annotated[list, operator.add] tells LangGraph to MERGE lists instead of replacing them.
# Without it, the last node's return would overwrite the whole list.

class AccumState(TypedDict):
    topic:  str
    steps:  Annotated[list[str], operator.add]   # merge, don't overwrite

def step_research(state: AccumState) -> AccumState:
    print("  [research]")
    return {"steps": [f"Researched: {state['topic']}"]}

def step_outline(state: AccumState) -> AccumState:
    print("  [outline]")
    return {"steps": ["Created outline with 3 sections"]}

def step_draft(state: AccumState) -> AccumState:
    print("  [draft]")
    return {"steps": ["Wrote first draft (200 words)"]}

b = StateGraph(AccumState)
b.add_node("research", step_research)
b.add_node("outline",  step_outline)
b.add_node("draft",    step_draft)
b.set_entry_point("research")
b.add_edge("research", "outline")
b.add_edge("outline",  "draft")
b.add_edge("draft",    END)
accum_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern B – Counters (each node increments a shared counter)
# ════════════════════════════════════════════════════════════════════════════════

class CountState(TypedDict):
    text:       str
    word_count: int
    char_count: int
    score:      float

def count_words(state: CountState) -> CountState:
    n = len(state["text"].split())
    print(f"  [count_words] {n} words")
    return {"word_count": n}

def count_chars(state: CountState) -> CountState:
    n = len(state["text"])
    print(f"  [count_chars] {n} chars")
    return {"char_count": n}

def compute_score(state: CountState) -> CountState:
    # Simple readability proxy: avg word length
    score = round(state["char_count"] / max(state["word_count"], 1), 2)
    print(f"  [compute_score] {score}")
    return {"score": score}

b = StateGraph(CountState)
b.add_node("words", count_words)
b.add_node("chars", count_chars)
b.add_node("score", compute_score)
b.set_entry_point("words")
b.add_edge("words", "chars")
b.add_edge("chars", "score")
b.add_edge("score", END)
counter_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern C – Partial updates (nodes only touch their own keys, others untouched)
# ════════════════════════════════════════════════════════════════════════════════

class PipelineState(TypedDict):
    raw:       str
    cleaned:   str
    summary:   str
    keywords:  list[str]
    done:      bool

def clean(state: PipelineState) -> PipelineState:
    cleaned = " ".join(state["raw"].split())   # collapse whitespace
    print(f"  [clean] '{state['raw'][:30]}...' → cleaned")
    return {"cleaned": cleaned}               # only updates 'cleaned', others unchanged

def summarize(state: PipelineState) -> PipelineState:
    resp = llm.invoke(f"Summarise in one sentence: {state['cleaned']}")
    print("  [summarize] done")
    return {"summary": resp.content}          # only updates 'summary'

def extract_keywords(state: PipelineState) -> PipelineState:
    resp = llm.invoke(f"List 3 keywords from this text, comma-separated: {state['cleaned']}")
    keywords = [k.strip() for k in resp.content.split(",")]
    print(f"  [keywords] {keywords}")
    return {"keywords": keywords, "done": True}  # updates keywords + done

b = StateGraph(PipelineState)
b.add_node("clean",    clean)
b.add_node("summarize",summarize)
b.add_node("keywords", extract_keywords)
b.set_entry_point("clean")
b.add_edge("clean",    "summarize")
b.add_edge("summarize","keywords")
b.add_edge("keywords", END)
pipeline_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern D – State persists across loop iterations
# ════════════════════════════════════════════════════════════════════════════════

class LoopState(TypedDict):
    number:    int
    history:   Annotated[list[int], operator.add]   # accumulates each iteration
    iterations: int

def double_it(state: LoopState) -> LoopState:
    new_val = state["number"] * 2
    print(f"  [double_it] {state['number']} → {new_val}")
    return {
        "number":     new_val,
        "history":    [new_val],     # appended to list, not replaced
        "iterations": state["iterations"] + 1
    }

def should_stop(state: LoopState) -> str:
    return "stop" if state["number"] >= 100 or state["iterations"] >= 5 else "continue"

b = StateGraph(LoopState)
b.add_node("double", double_it)
b.set_entry_point("double")
b.add_conditional_edges("double", should_stop, {"continue": "double", "stop": END})
loop_app = b.compile()


# ── Run all patterns ──────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Save graph PNGs
    for name, app in [
        ("06a_accum",    accum_app),
        ("06b_counter",  counter_app),
        ("06c_pipeline", pipeline_app),
        ("06d_loop",     loop_app),
    ]:
        path = f"../graphs/{name}.png"
        with open(path, "wb") as f:
            f.write(app.get_graph().draw_mermaid_png())
        print(f"Graph saved → {path}")

    print("\n" + "="*60)
    print("Pattern A – Accumulating list")
    print("="*60)
    result = accum_app.invoke({"topic": "machine learning", "steps": []})
    print("steps recorded:", result["steps"])

    print("\n" + "="*60)
    print("Pattern B – Counters")
    print("="*60)
    result = counter_app.invoke({"text": "LangGraph makes it easy to build stateful AI workflows.", "word_count": 0, "char_count": 0, "score": 0.0})
    print(f"words={result['word_count']}  chars={result['char_count']}  avg_word_len={result['score']}")

    print("\n" + "="*60)
    print("Pattern C – Partial updates (each node only touches its keys)")
    print("="*60)
    result = pipeline_app.invoke({
        "raw": "  LangGraph  is  a library   for  building  stateful  AI  apps.  ",
        "cleaned": "", "summary": "", "keywords": [], "done": False
    })
    print(f"cleaned  : {result['cleaned']}")
    print(f"summary  : {result['summary']}")
    print(f"keywords : {result['keywords']}")
    print(f"done     : {result['done']}")

    print("\n" + "="*60)
    print("Pattern D – State persists across loop iterations")
    print("="*60)
    result = loop_app.invoke({"number": 3, "history": [3], "iterations": 0})
    print(f"final number : {result['number']}")
    print(f"history      : {result['history']}")
    print(f"iterations   : {result['iterations']}")
