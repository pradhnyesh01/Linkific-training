"""
02_tool_chaining.py
Multi-Tool Agent Scenarios

Shows the LLM chaining multiple tool calls in a single conversation.
The agent automatically decides which tools to use and in what order.

Scenarios:
  A) Weather + Datetime  — "What's the weather in Paris and what day is it?"
  B) Database + Calculator — "What is the average marks and who scores highest?"
  C) File Reader + Data Analyzer — combined file analysis question
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_calling import run_agent

SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "..", "sample_data")


def print_chain_summary(result: dict):
    """Print which tools were called in sequence."""
    print(f"\n  Tools used ({len(result['tool_calls_made'])} calls):")
    for i, call in enumerate(result["tool_calls_made"], 1):
        status = "✓" if call["result"].get("success") else "✗"
        print(f"    {i}. {status} {call['tool']}  args={list(call['args'].keys())}")
    print(f"\n  Iterations : {result['iterations']}")
    print(f"  Tokens used: {result['total_tokens']}")


# ── Scenario A: Weather + Datetime ────────────────────────────────────────────

print("\n" + "="*60)
print("Scenario A — Weather + Datetime")
print("="*60)

result_a = run_agent(
    "What is the current weather in Tokyo (in Celsius), "
    "and what day of the week is 2026-04-17?",
    verbose=True,
)
print_chain_summary(result_a)


# ── Scenario B: Database + Calculator ────────────────────────────────────────

print("\n" + "="*60)
print("Scenario B — Database + Calculator")
print("="*60)

result_b = run_agent(
    "Query the students database to get the average marks, "
    "and also tell me what 90 is as a percentage of 100.",
    verbose=True,
)
print_chain_summary(result_b)


# ── Scenario C: File + Data Analyzer ─────────────────────────────────────────

print("\n" + "="*60)
print("Scenario C — File Reader + Data Analyzer")
print("="*60)

csv_path = os.path.abspath(os.path.join(SAMPLE_DATA, "sample.csv"))

result_c = run_agent(
    f"Read the file at {csv_path} and then analyze it to show "
    f"the value counts for the 'course' column.",
    verbose=True,
)
print_chain_summary(result_c)


# ── Summary ───────────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("Chaining Summary")
print("="*60)
for label, result in [("A (Weather+Datetime)", result_a),
                       ("B (DB+Calculator)",    result_b),
                       ("C (File+Analyze)",     result_c)]:
    n = len(result["tool_calls_made"])
    print(f"  Scenario {label}: {n} tool call(s), {result['iterations']} LLM call(s)")
