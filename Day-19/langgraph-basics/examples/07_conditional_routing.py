"""
Example 7 – Conditional Routing (comprehensive)
Shows four routing patterns:
  A) Binary routing   – two possible paths
  B) Multi-way routing – 4+ possible paths from one node
  C) Chained routing  – routing decision at multiple nodes in sequence
  D) Dynamic routing  – LLM decides the route at runtime
"""

import os
from dotenv import load_dotenv, find_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ════════════════════════════════════════════════════════════════════════════════
# Pattern A – Binary routing (two paths based on a simple condition)
# ════════════════════════════════════════════════════════════════════════════════

class BinaryState(TypedDict):
    number: int
    result: str

def check_even(state: BinaryState) -> str:
    """Router: returns 'even' or 'odd'."""
    return "even" if state["number"] % 2 == 0 else "odd"

b = StateGraph(BinaryState)
b.add_node("check",     lambda s: s)
b.add_node("even_node", lambda s: {"result": f"{s['number']} is even"})
b.add_node("odd_node",  lambda s: {"result": f"{s['number']} is odd"})
b.set_entry_point("check")
b.add_conditional_edges("check", check_even, {"even": "even_node", "odd": "odd_node"})
b.add_edge("even_node", END)
b.add_edge("odd_node",  END)
binary_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern B – Multi-way routing (4 paths based on priority level)
# ════════════════════════════════════════════════════════════════════════════════

class TicketState(TypedDict):
    issue:    str
    priority: str
    response: str

def classify_priority(state: TicketState) -> TicketState:
    prompt = (
        "Classify this support ticket priority as exactly one of: "
        "'critical', 'high', 'medium', or 'low'. One word only.\n"
        f"Ticket: {state['issue']}"
    )
    priority = llm.invoke(prompt).content.strip().lower()
    print(f"  [classify] → {priority}")
    return {"priority": priority}

def route_priority(state: TicketState) -> str:
    p = state["priority"]
    if "critical" in p: return "critical"
    if "high"     in p: return "high"
    if "medium"   in p: return "medium"
    return "low"

def handle_critical(state: TicketState) -> TicketState:
    return {"response": "🚨 CRITICAL: Paging on-call engineer immediately."}

def handle_high(state: TicketState) -> TicketState:
    return {"response": "⚠️ HIGH: Assigned to senior agent, response within 1 hour."}

def handle_medium(state: TicketState) -> TicketState:
    return {"response": "📋 MEDIUM: Added to queue, response within 24 hours."}

def handle_low(state: TicketState) -> TicketState:
    return {"response": "📌 LOW: Logged. We'll get back to you within 3 business days."}

b = StateGraph(TicketState)
b.add_node("classify", classify_priority)
b.add_node("critical", handle_critical)
b.add_node("high",     handle_high)
b.add_node("medium",   handle_medium)
b.add_node("low",      handle_low)
b.set_entry_point("classify")
b.add_conditional_edges("classify", route_priority,
    {"critical": "critical", "high": "high", "medium": "medium", "low": "low"})
for n in ["critical", "high", "medium", "low"]:
    b.add_edge(n, END)
multiway_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern C – Chained routing (routing decisions at two separate nodes)
# ════════════════════════════════════════════════════════════════════════════════
# Node 1 routes by language (english / other)
# Node 2 routes by formality (formal / casual)
# Only English text goes through the formality check.

class ChainedState(TypedDict):
    text:     str
    language: str
    tone:     str
    reply:    str

def detect_language(state: ChainedState) -> ChainedState:
    prompt = "Is this text English or another language? Reply 'english' or 'other'.\n" + state["text"]
    lang   = llm.invoke(prompt).content.strip().lower()
    print(f"  [detect_language] → {lang}")
    return {"language": lang}

def route_language(state: ChainedState) -> str:
    return "english" if "english" in state["language"] else "other"

def detect_tone(state: ChainedState) -> ChainedState:
    prompt = "Is this text formal or casual? Reply 'formal' or 'casual'.\n" + state["text"]
    tone   = llm.invoke(prompt).content.strip().lower()
    print(f"  [detect_tone] → {tone}")
    return {"tone": tone}

def route_tone(state: ChainedState) -> str:
    return "formal" if "formal" in state["tone"] else "casual"

def reply_formal(state: ChainedState) -> ChainedState:
    return {"reply": "Thank you for your enquiry. We will respond within one business day."}

def reply_casual(state: ChainedState) -> ChainedState:
    return {"reply": "Hey! Thanks for reaching out — we'll get back to you soon 👋"}

def reply_translate(state: ChainedState) -> ChainedState:
    return {"reply": "We noticed your message may be in another language. Please contact support@example.com."}

b = StateGraph(ChainedState)
b.add_node("lang_check",  detect_language)
b.add_node("tone_check",  detect_tone)
b.add_node("formal",      reply_formal)
b.add_node("casual",      reply_casual)
b.add_node("translate",   reply_translate)

b.set_entry_point("lang_check")
b.add_conditional_edges("lang_check", route_language,
    {"english": "tone_check", "other": "translate"})   # first routing decision
b.add_conditional_edges("tone_check", route_tone,
    {"formal": "formal", "casual": "casual"})           # second routing decision
for n in ["formal", "casual", "translate"]:
    b.add_edge(n, END)
chained_app = b.compile()


# ════════════════════════════════════════════════════════════════════════════════
# Pattern D – Dynamic routing (LLM decides route at runtime)
# ════════════════════════════════════════════════════════════════════════════════

class DynamicState(TypedDict):
    question:   str
    route:      str
    answer:     str

def llm_router_node(state: DynamicState) -> DynamicState:
    """LLM reads the question and decides which specialist to use."""
    prompt = (
        "You are a router. Read the question and decide which specialist should answer it.\n"
        "Reply with exactly one word: 'math', 'history', 'science', or 'general'.\n"
        f"Question: {state['question']}"
    )
    route = llm.invoke(prompt).content.strip().lower()
    print(f"  [llm_router] → {route}")
    return {"route": route}

def route_by_llm(state: DynamicState) -> str:
    r = state["route"]
    if "math"    in r: return "math"
    if "history" in r: return "history"
    if "science" in r: return "science"
    return "general"

def math_specialist(state: DynamicState) -> DynamicState:
    resp = llm.invoke(f"Answer this math question precisely: {state['question']}")
    return {"answer": f"[MATH] {resp.content}"}

def history_specialist(state: DynamicState) -> DynamicState:
    resp = llm.invoke(f"Answer this history question with context: {state['question']}")
    return {"answer": f"[HISTORY] {resp.content}"}

def science_specialist(state: DynamicState) -> DynamicState:
    resp = llm.invoke(f"Answer this science question with a clear explanation: {state['question']}")
    return {"answer": f"[SCIENCE] {resp.content}"}

def general_handler(state: DynamicState) -> DynamicState:
    resp = llm.invoke(state["question"])
    return {"answer": f"[GENERAL] {resp.content}"}

b = StateGraph(DynamicState)
b.add_node("router",  llm_router_node)
b.add_node("math",    math_specialist)
b.add_node("history", history_specialist)
b.add_node("science", science_specialist)
b.add_node("general", general_handler)
b.set_entry_point("router")
b.add_conditional_edges("router", route_by_llm,
    {"math":"math","history":"history","science":"science","general":"general"})
for n in ["math","history","science","general"]:
    b.add_edge(n, END)
dynamic_app = b.compile()


# ── Run all patterns ──────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Save PNGs
    for name, app in [
        ("07a_binary",   binary_app),
        ("07b_multiway", multiway_app),
        ("07c_chained",  chained_app),
        ("07d_dynamic",  dynamic_app),
    ]:
        path = f"../graphs/{name}.png"
        with open(path, "wb") as f:
            f.write(app.get_graph().draw_mermaid_png())
        print(f"Graph saved → {path}")

    print("\n" + "="*60)
    print("Pattern A – Binary routing")
    print("="*60)
    for n in [4, 7]:
        r = binary_app.invoke({"number": n, "result": ""})
        print(r["result"])

    print("\n" + "="*60)
    print("Pattern B – Multi-way routing (4 priority levels)")
    print("="*60)
    tickets = [
        "The entire production server is down and users cannot login!",
        "The export button is misaligned on the settings page.",
    ]
    for issue in tickets:
        print(f"\nIssue: {issue}")
        r = multiway_app.invoke({"issue": issue, "priority": "", "response": ""})
        print(r["response"])

    print("\n" + "="*60)
    print("Pattern C – Chained routing (language → tone)")
    print("="*60)
    texts = [
        "Dear Sir, I would like to formally request an update on my application.",
        "hey! any update on my order? been waiting forever lol",
    ]
    for text in texts:
        print(f"\nText: {text}")
        r = chained_app.invoke({"text": text, "language": "", "tone": "", "reply": ""})
        print(f"Reply: {r['reply']}")

    print("\n" + "="*60)
    print("Pattern D – Dynamic routing (LLM picks the specialist)")
    print("="*60)
    questions = [
        "What is the square root of 144?",
        "Who was the first Prime Minister of India?",
        "Why is the sky blue?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        r = dynamic_app.invoke({"question": q, "route": "", "answer": ""})
        print(f"A: {r['answer'][:120]}")
