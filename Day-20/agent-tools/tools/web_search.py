"""
tools/web_search.py
Tool 2 – Web Search

Searches the internet via DuckDuckGo (free, no API key required).
Returns top N results with title, URL, and a short snippet.

Flow: execute(args) → search_web(query, max_results) → {"success": True/False, ...}

Dependency: pip install duckduckgo-search
"""

import time
from typing import Any


# ── Core function ─────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 5) -> dict[str, Any]:
    """
    Run a DuckDuckGo text search.

    Args:
        query       : search string
        max_results : number of results to return (1–10)

    Returns:
        {"success": True,  "query": str, "num_results": int, "results": [...]}
        {"success": False, "error": str}
    """
    if not query or not query.strip():
        return {"success": False, "error": "Query cannot be empty."}

    max_results = max(1, min(int(max_results), 10))   # clamp 1–10

    # Support both old package name (duckduckgo-search) and new name (ddgs)
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

    # Retry once on failure (handles occasional rate limits)
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



if __name__ == "__main__":
    import json

    tests = [
        {"query": "OpenAI function calling tutorial", "max_results": 3},
        {"query": "LangGraph vs LangChain",           "max_results": 2},
        {"query": ""},    # error case
    ]

    for t in tests:
        result = execute(t)
        if result["success"]:
            print(f"Query: {result['query']} → {result['num_results']} results")
            for r in result["results"]:
                print(f"  • {r['title']}")
                print(f"    {r['url']}")
        else:
            print(f"Error: {result['error']}")
        print()
