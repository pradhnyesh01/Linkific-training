"""
agents/critic.py
Critic Agent — evaluates the analysis and decides routing.

Adapted from Day-22 with one key addition:
  Sets routing_decision = "approved" | "needs_more_research"
  LangGraph uses this to either move to Writer or loop back to Researcher.

Input:  state.topic, state.analysis, state.iteration
Output: state.critique, state.routing_decision
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """
    Critically reviews the Analyzer's output.

    Unlike Day-22, this Critic also decides routing:
      - "approved"              → analysis is good enough → Writer
      - "needs_more_research"   → critical gaps → loop back to Researcher
    """

    def __init__(self):
        super().__init__(
            name  = "Critic",
            role  = "You are a rigorous editor and fact-checker. Evaluate research analyses for quality and completeness. Be direct and constructive.",
        )

    def run(self, state) -> dict:
        state.add_log(self.name, "Reviewing the analysis...")

        if not state.analysis:
            state.add_log(self.name, "Warning: no analysis found.")
            state.critique         = "No analysis available to critique."
            state.routing_decision = "approved"   # nothing to re-research
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
                    f"2. Any vague or unsupported claims\n"
                    f"3. Specific suggestions for improvement\n"
                    f"4. Overall quality: strong / adequate / weak\n\n"
                    f"After your critique, on the very last line write exactly one of:\n"
                    f"ROUTING: approved\n"
                    f"ROUTING: needs_more_research\n\n"
                    f"Use 'needs_more_research' only if the analysis is missing critical "
                    f"information that a new web search would fix. "
                    f"Use 'approved' if the analysis is adequate or better."
                ),
            },
        ]

        raw = self._chat(messages)

        # ── Parse routing decision from last line ──────────────────────────────
        routing = "approved"   # safe default
        lines   = raw.strip().splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("ROUTING:"):
                decision = line.split(":", 1)[1].strip().lower()
                if decision in ("approved", "needs_more_research"):
                    routing = decision
                break

        # Strip the ROUTING line from the critique text
        critique_lines = [l for l in lines if not l.strip().startswith("ROUTING:")]
        state.critique         = "\n".join(critique_lines).strip()
        state.routing_decision = routing

        state.add_log(
            self.name,
            f"Critique complete. Routing decision: {routing} "
            f"(iteration {state.iteration})"
        )
        return state
