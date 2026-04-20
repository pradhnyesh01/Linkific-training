"""
agents/coordinator.py
Coordinator Agent — orchestrates the full multi-agent pipeline.

No LLM calls — pure Python orchestration logic.
Runs agents in a fixed sequence and passes state between them.

Pipeline:
  ResearcherAgent → AnalyzerAgent → CriticAgent → WriterAgent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
from state import ResearchState
from agents.researcher import ResearcherAgent
from agents.analyzer   import AnalyzerAgent
from agents.critic     import CriticAgent
from agents.writer     import WriterAgent

class CoordinatorAgent:
    """
    Orchestrates the 4 worker agents in sequence.

    Usage:
        coordinator = CoordinatorAgent()
        state = coordinator.run("impact of AI on healthcare")
        print(state.final_report)
    """

    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyzer   = AnalyzerAgent()
        self.critic     = CriticAgent()
        self.writer     = WriterAgent()

        # Pipeline order
        self.pipeline = [
            self.researcher,
            self.analyzer,
            self.critic,
            self.writer,
        ]

    def run(self, topic: str) -> ResearchState:
        """
        Run the full research pipeline for a given topic.

        Args:
            topic: The research topic (e.g. "impact of AI on healthcare")

        Returns:
            Fully populated ResearchState with final_report ready.
        """
        print(f"\n{'='*60}")
        print(f"  Multi-Agent Research Assistant")
        print(f"  Topic: {topic}")
        print(f"{'='*60}\n")

        state = ResearchState(topic=topic)
        total_start = time.perf_counter()

        for agent in self.pipeline:
            step_start = time.perf_counter()
            print(f"── {agent.name} Agent ──────────────────────────")
            state = agent.run(state)
            elapsed = time.perf_counter() - step_start
            print(f"   Done in {elapsed:.1f}s\n")

        total_elapsed = time.perf_counter() - total_start
        print(f"{'='*60}")
        print(f"  Pipeline complete in {total_elapsed:.1f}s")
        print(f"  Search results : {len(state.search_results)}")
        print(f"  Report length  : {len(state.final_report)} chars")
        print(f"{'='*60}\n")

        return state