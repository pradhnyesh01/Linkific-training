"""
agents/researcher.py
Researcher Agent — searches the web for information on the given topic.

Uses OpenAI function calling so the model decides:
  - what to search for
  - how many searches to run
  - when it has enough information

Tool: web_search 

Input:  state.topic
Output: state.search_results  (list of {title, url, snippet})
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent
from state import ResearchState
from tools.web_search import execute as web_search_execute


# ── OpenAI function schema for web_search ─────────────────────────────────────

WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information on a topic using DuckDuckGo. Returns titles, URLs, and snippets.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type":        "string",
                    "description": "The search query string",
                },
                "max_results": {
                    "type":        "integer",
                    "description": "Number of results to return (1–10)",
                    "default":     5,
                },
            },
            "required": ["query"],
        },
    },
}


class ResearcherAgent(BaseAgent):
    """
    Searches the web for information about the research topic.

    Uses function calling — the model decides what queries to run.
    Collects all search results into state.search_results.
    """

    def __init__(self):
        super().__init__(
            name  = "Researcher",
            role  = "You are a research specialist. Your job is to search the web and gather comprehensive, relevant information on a given topic. Use multiple targeted searches to cover different aspects of the topic.",
        )

    def _tool_executor(self, tool_name: str, args: dict) -> dict:
        """Dispatch tool calls from the LLM."""
        if tool_name == "web_search":
            return web_search_execute(args)
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def run(self, state: ResearchState) -> ResearchState:
        state.status = "researching"
        state.add_log(self.name, f"Researching topic: '{state.topic}'")

        messages = [
            {
                "role":    "system",
                "content": self.role,
            },
            {
                "role":    "user",
                "content": (
                    f"Research this topic thoroughly: {state.topic}\n\n"
                    f"Use the web_search tool to find relevant information. "
                    f"Run 2-3 searches with different angles to get comprehensive coverage. "
                    f"After searching, summarise what sources you found."
                ),
            },
        ]

        _, tool_calls = self._chat_with_tools(
            messages = messages,
            tools    = [WEB_SEARCH_SCHEMA],
            executor = self._tool_executor,
        )

        # Collect all search results from tool calls
        all_results = []
        for tc in tool_calls:
            if tc["name"] == "web_search" and tc["result"].get("success"):
                all_results.extend(tc["result"].get("results", []))

        # Deduplicate by URL
        seen = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique_results.append(r)

        state.search_results = unique_results
        state.add_log(self.name, f"Found {len(unique_results)} unique results from {len(tool_calls)} searches.")
        return state
