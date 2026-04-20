"""
agents/critic.py
Critic Agent — evaluates the analysis and flags weaknesses.

No tools — pure LLM reasoning.

Input:  state.topic, state.analysis
Output: state.critique  (gaps, unsupported claims, improvement suggestions)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent
from state import ResearchState

class CriticAgent(BaseAgent):
    """
    Critically reviews the Analyzer's output.
    Identifies gaps, vague claims, missing context, and areas to improve.
    The Writer uses this critique to produce a better final report.
    """

    def __init__(self):
        super().__init__(
            name  = "Critic",
            role  = "You are a rigorous editor and fact-checker. Your job is to critically evaluate an analysis and identify: gaps in coverage, unsupported or vague claims, missing context, logical inconsistencies, and specific areas that need more depth. Be direct and constructive.",
        )

    def run(self, state: ResearchState) -> ResearchState:
        state.status = "critiquing"
        state.add_log(self.name, "Reviewing the analysis...")

        if not state.analysis:
            state.critique = "No analysis available to critique."
            state.add_log(self.name, "Warning: no analysis found.")
            return state

        messages = [
            {
                "role":    "system",
                "content": self.role,
            },
            {
                "role":    "user",
                "content": (
                    f"Topic: {state.topic}\n\n"
                    f"Analysis to review:\n{state.analysis}\n\n"
                    f"Provide a critique covering:\n"
                    f"1. What's missing or underexplored\n"
                    f"2. Any claims that seem vague or unsupported\n"
                    f"3. Specific suggestions for improvement\n"
                    f"4. Overall quality assessment (strong / adequate / weak)\n\n"
                    f"Be specific and actionable. The Writer will use your feedback."
                ),
            },
        ]

        state.critique = self._chat(messages)
        state.add_log(self.name, f"Critique complete ({len(state.critique)} chars).")
        return state
