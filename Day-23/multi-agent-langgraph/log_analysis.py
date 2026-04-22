"""
log_analysis.py
Analyses log files produced by the multi-agent pipeline.

Reads all agent_YYYYMMDD.log files from the logs/ directory and prints:
  - Total pipeline runs
  - Per-agent call counts
  - Routing decisions breakdown
  - Tool calls made
  - Errors and warnings

Run:
    python log_analysis.py
    python log_analysis.py --date 20240422   (specific day)
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


# ── Log parsers ───────────────────────────────────────────────────────────────

def parse_log_file(filepath: str) -> list[dict]:
    """Parse a log file into a list of structured entries."""
    entries = []
    pattern = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| "
        r"(?P<level>\w+)\s+\| "
        r"(?P<logger>[^\|]+)\| "
        r"(?P<message>.+)"
    )
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                entries.append({
                    "timestamp": m.group("timestamp"),
                    "level":     m.group("level").strip(),
                    "logger":    m.group("logger").strip(),
                    "message":   m.group("message").strip(),
                })
    return entries


def load_logs(date_filter: str | None = None) -> list[dict]:
    """Load all log files (optionally filtered by date string YYYYMMDD)."""
    if not os.path.isdir(LOG_DIR):
        return []

    all_entries = []
    for fname in sorted(os.listdir(LOG_DIR)):
        if not fname.endswith(".log"):
            continue
        if date_filter and date_filter not in fname:
            continue
        filepath = os.path.join(LOG_DIR, fname)
        all_entries.extend(parse_log_file(filepath))

    return all_entries


# ── Analysis functions ────────────────────────────────────────────────────────

def count_pipeline_runs(entries: list[dict]) -> int:
    return sum(1 for e in entries if "Pipeline started" in e["message"])


def agent_call_counts(entries: list[dict]) -> dict:
    counts = defaultdict(int)
    for e in entries:
        if e["logger"].startswith("agent."):
            agent = e["logger"].replace("agent.", "").capitalize()
            if "LLM call" in e["message"]:
                counts[agent] += 1
    return dict(counts)


def routing_decisions(entries: list[dict]) -> dict:
    counts = defaultdict(int)
    for e in entries:
        if "Routing decision:" in e["message"]:
            decision = e["message"].split("Routing decision:")[-1].strip().split()[0]
            counts[decision] += 1
    return dict(counts)


def tool_calls(entries: list[dict]) -> list[str]:
    return [e["message"] for e in entries if e["message"].startswith("Tool call →")]


def errors_and_warnings(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e["level"] in ("ERROR", "WARNING")]


def cost_summaries(entries: list[dict]) -> list[str]:
    return [e["message"] for e in entries if "Run complete" in e["message"]]


# ── Report printer ────────────────────────────────────────────────────────────

def print_report(entries: list[dict]):
    if not entries:
        print("No log entries found. Run the pipeline first to generate logs.")
        return

    print(f"\n{'='*55}")
    print("  Log Analysis Report")
    print(f"  Analysed {len(entries)} log entries")
    print(f"{'='*55}")

    # Pipeline runs
    runs = count_pipeline_runs(entries)
    print(f"\n  Pipeline runs        : {runs}")

    # Agent LLM calls
    calls = agent_call_counts(entries)
    if calls:
        print(f"\n  Agent LLM calls:")
        for agent, count in sorted(calls.items()):
            print(f"    {agent:<15} {count} call(s)")

    # Routing decisions
    routing = routing_decisions(entries)
    if routing:
        print(f"\n  Routing decisions:")
        for decision, count in routing.items():
            print(f"    {decision:<25} {count}x")

    # Tool calls
    tools = tool_calls(entries)
    if tools:
        print(f"\n  Tool calls ({len(tools)} total):")
        for t in tools[:10]:   # show first 10
            print(f"    {t}")
        if len(tools) > 10:
            print(f"    ... and {len(tools) - 10} more")

    # Costs
    costs = cost_summaries(entries)
    if costs:
        print(f"\n  Cost summaries:")
        for c in costs:
            print(f"    {c}")

    # Errors
    errs = errors_and_warnings(entries)
    if errs:
        print(f"\n  Errors / Warnings ({len(errs)}):")
        for e in errs:
            print(f"    [{e['level']}] {e['timestamp']} — {e['message']}")
    else:
        print(f"\n  No errors or warnings found.")

    print(f"\n{'='*55}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    date_filter = None
    if len(sys.argv) > 1 and sys.argv[1] == "--date":
        date_filter = sys.argv[2] if len(sys.argv) > 2 else None

    entries = load_logs(date_filter)
    print_report(entries)
