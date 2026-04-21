"""
agents/analyzer.py
Analyzer Agent — reads search results and writes a concise analysis.

No tools — pure LLM reasoning over the gathered search snippets.

Input:  state.topic, state.search_results
Output: state.analysis  (plain text summary with key facts and themes)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent
from state import ResearchState


class AnalyzerAgent(BaseAgent):
    """
    Reads the raw search results from the Researcher and produces
    a structured analysis: key facts, main themes, important takeaways.
    """

    def __init__(self):
        super().__init__(
            name  = "Analyzer",
            role  = "You are an expert analyst. Your job is to read raw search results and extract meaningful insights — key facts, recurring themes, important statistics, and clear takeaways. Be concise and well-organised.",
        )

    def run(self, state: ResearchState) -> ResearchState:
        state.status = "analyzing"
        state.add_log(self.name, "Analyzing search results...")

        if not state.search_results:
            state.analysis = "No search results available to analyze."
            state.add_log(self.name, "Warning: no search results found.")
            return state

        # Format search results into a readable block for the LLM
        results_text = "\n\n".join([
            f"Source {i+1}: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
            for i, r in enumerate(state.search_results)
        ])

        messages = [
            {
                "role":    "system",
                "content": self.role,
            },
            {
                "role":    "user",
                "content": (
                    f"Topic: {state.topic}\n\n"
                    f"Search Results:\n{results_text}\n\n"
                    f"Write a concise analysis covering:\n"
                    f"1. Key facts and findings\n"
                    f"2. Main themes and patterns\n"
                    f"3. Important statistics or data points (if any)\n"
                    f"4. Key takeaways\n\n"
                    f"Keep it focused and factual. 3–5 paragraphs."
                ),
            },
        ]

        state.analysis = self._chat(messages)
        state.add_log(self.name, f"Analysis complete ({len(state.analysis)} chars).")
        return state
