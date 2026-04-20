"""
agents/writer.py
Writer Agent — produces the final formatted markdown research report.

No tools — takes the analysis + critique and writes a polished report.

Input:  state.topic, state.analysis, state.critique
Output: state.final_report  (well-structured markdown)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent
from state import ResearchState


class WriterAgent(BaseAgent):
    """
    Produces the final research report in markdown format.
    Uses the Analyzer's findings and addresses the Critic's feedback.
    """

    def __init__(self):
        super().__init__(
            name  = "Writer",
            role  = "You are a professional technical writer. Your job is to synthesize research and analysis into a clear, well-structured markdown report. Address any gaps or weaknesses flagged by the critic. Write for an informed but general audience.",
        )

    def run(self, state: ResearchState) -> ResearchState:
        state.status = "writing"
        state.add_log(self.name, "Writing the final report...")

        if not state.analysis:
            state.final_report = f"# {state.topic}\n\nInsufficient research data to generate a report."
            state.add_log(self.name, "Warning: no analysis to write from.")
            return state

        messages = [
            {
                "role":    "system",
                "content": self.role,
            },
            {
                "role":    "user",
                "content": (
                    f"Write a research report on: {state.topic}\n\n"
                    f"--- ANALYSIS ---\n{state.analysis}\n\n"
                    f"--- CRITIC FEEDBACK ---\n{state.critique}\n\n"
                    f"Instructions:\n"
                    f"- Use markdown formatting (headings, bullet points, bold)\n"
                    f"- Structure: Title, Executive Summary, Key Findings, "
                    f"  Detailed Analysis, Conclusion\n"
                    f"- Address the critic's concerns and fill in the gaps\n"
                    f"- Keep the tone professional and objective\n"
                    f"- Aim for 400–600 words"
                ),
            },
        ]

        state.final_report = self._chat(messages)
        state.status = "done"
        state.add_log(self.name, f"Report complete ({len(state.final_report)} chars).")
        return state
