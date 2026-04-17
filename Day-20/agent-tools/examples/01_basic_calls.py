"""
01_basic_calls.py
Direct Tool Testing — No LLM Involved

Calls execute() on each of the 8 tools directly.
Shows both a success case and an error case per tool.
This is the fastest way to verify that all tools work correctly.

Flow: import tool → call execute(args) → print result
"""

import sys
import os
import json

# Add parent directory to path so tools/ and tool_schemas can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.calculator     import execute as calc
from tools.web_search     import execute as search
from tools.database_query import execute as dbq
from tools.file_reader    import execute as fread
from tools.weather        import execute as weather
from tools.email_sender   import execute as email
from tools.datetime_tool  import execute as dt
from tools.data_analyzer  import execute as analyze

SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "..", "sample_data")


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")

def show(label: str, result: dict):
    status = "✓ SUCCESS" if result.get("success") else "✗ ERROR  "
    print(f"\n  [{status}] {label}")
    if result.get("success"):
        # Print key fields, not the whole dict
        for k, v in result.items():
            if k not in ("success",):
                val = str(v)
                print(f"    {k}: {val[:100]}{'...' if len(val)>100 else ''}")
    else:
        print(f"    error: {result.get('error')}")


# ── Tool 1: Calculator ────────────────────────────────────────────────────────

section("Tool 1 – Calculator")

show("15% of 847",        calc({"operation": "percentage", "a": 15,  "b": 847}))
show("sqrt(144)",         calc({"operation": "sqrt",       "a": 144}))
show("divide by zero",    calc({"operation": "divide",     "a": 10,  "b": 0}))
show("unknown operation", calc({"operation": "modulo",     "a": 10,  "b": 3}))


# ── Tool 2: Web Search ────────────────────────────────────────────────────────

section("Tool 2 – Web Search")

result = search({"query": "Python function calling OpenAI", "max_results": 3})
if result["success"]:
    print(f"\n  ✓ SUCCESS  Found {result['num_results']} results for: {result['query']}")
    for r in result["results"]:
        print(f"    • {r['title'][:60]}")
else:
    print(f"\n  ✗ ERROR  {result['error']}")

show("empty query (error)",  search({"query": ""}))


# ── Tool 3: Database Query ────────────────────────────────────────────────────

section("Tool 3 – Database Query")

result = dbq({"limit": 5})
if result["success"]:
    print(f"\n  ✓ SUCCESS  Returned {result['row_count']} rows")
    for r in result["rows"][:3]:
        print(f"    {r}")
else:
    print(f"\n  ✗ ERROR  {result['error']}")

result2 = dbq({"aggregate": "avg_marks"})
if result2["success"]:
    print(f"\n  ✓ SUCCESS  avg_marks = {result2['result']:.2f}")
else:
    print(f"\n  ✗ ERROR  {result2['error']}")

show("invalid column (error)", dbq({"filter_by": "hacker_column", "filter_value": "x"}))


# ── Tool 4: File Reader ───────────────────────────────────────────────────────

section("Tool 4 – File Reader")

show("sample.txt (5 lines)", fread({"file_path": os.path.join(SAMPLE_DATA, "sample.txt"), "max_lines": 5}))
show("sample.csv (3 rows)",  fread({"file_path": os.path.join(SAMPLE_DATA, "sample.csv"), "max_lines": 3}))
show("sample.json",          fread({"file_path": os.path.join(SAMPLE_DATA, "sample.json")}))
show("missing file (error)", fread({"file_path": "/nonexistent/file.txt"}))
show("unsupported .pdf (error)", fread({"file_path": os.path.join(SAMPLE_DATA, "dummy.pdf")}))


# ── Tool 5: Weather ───────────────────────────────────────────────────────────

section("Tool 5 – Weather")

for city in ["London", "Mumbai"]:
    r = weather({"city": city, "units": "celsius"})
    if r["success"]:
        print(f"\n  ✓ SUCCESS  {r['city']}, {r['country']}: "
              f"{r['temperature']}{r['temperature_unit']}  {r['condition']}")
    else:
        print(f"\n  ✗ ERROR    {r['error']}")

show("nonexistent city (error)", weather({"city": "Xyzabc123notacity"}))


# ── Tool 6: Email Sender ──────────────────────────────────────────────────────

section("Tool 6 – Email Sender (Simulation)")

show("normal email", email({
    "to":      "alice@example.com",
    "subject": "Meeting Tomorrow",
    "body":    "Hi Alice, just a reminder about our 10am meeting.",
}))
show("high priority + CC", email({
    "to":       "boss@company.com",
    "subject":  "Server Outage",
    "body":     "Production is down. Investigating.",
    "cc":       "devops@company.com",
    "priority": "high",
}))
show("bad email (error)",   email({"to": "not-valid", "subject": "X", "body": "Y"}))
show("empty subject (error)", email({"to": "a@b.com",  "subject": "",  "body": "Y"}))


# ── Tool 7: Datetime ──────────────────────────────────────────────────────────

section("Tool 7 – Datetime")

show("now (UTC)",                    dt({"operation": "now"}))
show("add 30 days to 2026-04-17",    dt({"operation": "add_days",    "date_str": "2026-04-17", "days": 30}))
show("day of week for 2026-01-01",   dt({"operation": "day_of_week", "date_str": "2026-01-01"}))
show("days between two dates",       dt({"operation": "days_between","date_str": "2026-01-01,2026-04-17"}))
show("is 2026-04-19 a weekend?",     dt({"operation": "is_weekend",  "date_str": "2026-04-19"}))
show("invalid date (error)",         dt({"operation": "add_days",    "date_str": "not-a-date",  "days": 1}))


# ── Tool 8: Data Analyzer ─────────────────────────────────────────────────────

section("Tool 8 – Data Analyzer")

csv_path = os.path.join(SAMPLE_DATA, "sample.csv")

result = analyze({"source": csv_path, "operation": "describe"})
if result["success"]:
    print(f"\n  ✓ SUCCESS  describe: shape={result['shape']}, columns={result['columns']}")
else:
    print(f"\n  ✗ ERROR  {result['error']}")

result = analyze({"source": csv_path, "operation": "value_counts", "column": "course"})
if result["success"]:
    print(f"\n  ✓ SUCCESS  value_counts[course]: {result['result']}")
else:
    print(f"\n  ✗ ERROR  {result['error']}")

result = analyze({"source": csv_path, "operation": "groupby", "group_by": "course"})
if result["success"]:
    print(f"\n  ✓ SUCCESS  groupby[course]: {len(result['result'])} groups")
    for row in result["result"]:
        print(f"    {row}")
else:
    print(f"\n  ✗ ERROR  {result['error']}")

show("unknown operation (error)", analyze({"source": csv_path, "operation": "pivot"}))
show("missing file (error)",      analyze({"source": "/no/file.csv"}))

print(f"\n{'='*60}")
print("  All 8 tools tested.")
print(f"{'='*60}\n")
