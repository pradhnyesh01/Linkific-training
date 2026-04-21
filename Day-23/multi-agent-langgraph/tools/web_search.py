"""
tools/web_search.py
Web Search Tool — copied from Day-20/agent-tools/tools/web_search.py

Searches the internet via DuckDuckGo (free, no API key required).
Returns top N results with title, URL, and snippet.
"""

import time
from typing import Any


def search_web(query: str, max_results: int = 5) -> dict[str, Any]:
    """
    Run a DuckDuckGo text search.

    Returns:
        {"success": True,  "query": str, "num_results": int, "results": [...]}
        {"success": False, "error": str}
    """
    if not query or not query.strip():
        return {"success": False, "error": "Query cannot be empty."}

    max_results = max(1, min(int(max_results), 10))

    DDGS = None
    for module_name in ("ddgs", "duckduckgo_search"):
        try:
            mod = __import__(module_name, fromlist=["DDGS"])
            DDGS = mod.DDGS
            break
        except ImportError:
            continue
    if DDGS is None:
        return {
            "success": False,
            "error":   "Search library not installed. Run: pip install ddgs",
        }

    for attempt in range(2):
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(query.strip(), max_results=max_results))
            break
        except Exception as e:
            if attempt == 0:
                time.sleep(1)
                continue
            return {"success": False, "error": f"Search failed: {e}"}

    results = [
        {
            "title":   r.get("title",   ""),
            "url":     r.get("href",    ""),
            "snippet": r.get("body",    ""),
        }
        for r in raw
    ]

    return {
        "success":     True,
        "query":       query.strip(),
        "num_results": len(results),
        "results":     results,
    }


def execute(args: dict) -> dict:
    return search_web(
        query       = args.get("query", ""),
        max_results = args.get("max_results", 5),
    )
