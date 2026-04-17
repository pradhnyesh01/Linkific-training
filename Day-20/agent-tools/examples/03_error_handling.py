"""
03_error_handling.py
Error Handling Examples

Tests how tools and the agent handle bad inputs gracefully.
Every error should return {"success": False, "error": "..."} — never raise.

Tests:
  1. Direct tool errors (bad args, missing files, invalid cities)
  2. Agent-level error recovery (agent sees the error and reports it)
  3. max_iterations cap
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.calculator     import execute as calc
from tools.web_search     import execute as search
from tools.database_query import execute as dbq
from tools.file_reader    import execute as fread
from tools.weather        import execute as weather
from tools.email_sender   import execute as email
from tools.datetime_tool  import execute as dt
from tools.data_analyzer  import execute as analyze
from function_calling     import run_agent


def check(label: str, result: dict, expect_success: bool = False):
    """Assert result matches expected success/failure and display it."""
    success = result.get("success", False)
    marker  = "✓" if success == expect_success else "✗ UNEXPECTED"
    status  = "SUCCESS" if success else "ERROR"
    print(f"\n  [{marker}] {label}")
    if success:
        print(f"    result keys: {list(result.keys())}")
    else:
        print(f"    error: {result.get('error')}")


print("\n" + "="*60)
print("Part 1 — Direct Tool Error Cases")
print("="*60)

# ── Calculator errors ─────────────────────────────────────────────────────────
print("\n  Calculator:")
check("divide by zero",     calc({"operation": "divide",  "a": 10, "b": 0}))
check("sqrt of negative",   calc({"operation": "sqrt",    "a": -4}))
check("unknown operation",  calc({"operation": "modulo",  "a": 7,  "b": 3}))
check("missing 'a'",        calc({"operation": "add"}))

# ── File reader errors ────────────────────────────────────────────────────────
print("\n  File Reader:")
check("file not found",         fread({"file_path": "/no/such/file.txt"}))
check("unsupported extension",  fread({"file_path": "/tmp/test.pdf"}))
check("empty path",             fread({"file_path": ""}))

# ── Database errors ───────────────────────────────────────────────────────────
print("\n  Database Query:")
check("invalid column name",    dbq({"filter_by": "hacker_col", "filter_value": "x"}))
check("invalid aggregate",      dbq({"aggregate": "sum_marks"}))
check("bad order_by column",    dbq({"order_by": "secret_col DESC"}))

# ── Weather errors ────────────────────────────────────────────────────────────
print("\n  Weather:")
check("nonexistent city",   weather({"city": "Xyzabc123notacity"}))
check("empty city",         weather({"city": ""}))

# ── Email errors ──────────────────────────────────────────────────────────────
print("\n  Email Sender:")
check("invalid email format",   email({"to": "notanemail", "subject": "X", "body": "Y"}))
check("empty subject",          email({"to": "a@b.com",    "subject": "",  "body": "Y"}))
check("empty body",             email({"to": "a@b.com",    "subject": "X", "body": ""}))

# ── Datetime errors ───────────────────────────────────────────────────────────
print("\n  Datetime Tool:")
check("unknown operation",  dt({"operation": "yesterday"}))
check("bad date format",    dt({"operation": "add_days", "date_str": "17-April-2026", "days": 1}))
check("missing days param", dt({"operation": "add_days", "date_str": "2026-04-17"}))

# ── Web search errors ─────────────────────────────────────────────────────────
print("\n  Web Search:")
check("empty query", search({"query": ""}))

# ── Data analyzer errors ──────────────────────────────────────────────────────
print("\n  Data Analyzer:")
check("file not found",        analyze({"source": "/no/file.csv"}))
check("unknown operation",     analyze({"source": "sample_data/sample.csv", "operation": "pivot"}))
check("missing group_by col",  analyze({"source": "sample_data/sample.csv", "operation": "groupby"}))


# ── Part 2: Agent-level error recovery ───────────────────────────────────────

print("\n" + "="*60)
print("Part 2 — Agent Error Recovery")
print("(The agent sees the error and gracefully reports it to the user)")
print("="*60)

# Agent gets an error from the tool and explains it to the user
result = run_agent(
    "What is the weather in ZzZzzNotARealCity999?",
    verbose=True,
)
print(f"\n  Tool error seen by agent: "
      f"{result['tool_calls_made'][0]['result'].get('error') if result['tool_calls_made'] else 'none'}")

result2 = run_agent(
    "Read the file at /this/does/not/exist.txt and summarize it.",
    verbose=True,
)
print(f"\n  Tool error seen by agent: "
      f"{result2['tool_calls_made'][0]['result'].get('error') if result2['tool_calls_made'] else 'none'}")


# ── Part 3: max_iterations cap ────────────────────────────────────────────────

print("\n" + "="*60)
print("Part 3 — max_iterations Safety Cap")
print("="*60)

result3 = run_agent(
    "What is 2+2? Then what is 3+3? Then 4+4? Then 5+5?",
    max_iterations=2,
    verbose=True,
)
print(f"\n  Stopped at iteration: {result3['iterations']}")
print(f"  Answer given: {result3['answer'][:100]}")


print("\n" + "="*60)
print("Error handling tests complete.")
print("All errors returned {'success': False, 'error': '...'} — no exceptions raised.")
print("="*60 + "\n")
