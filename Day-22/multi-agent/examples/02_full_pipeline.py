"""
02_full_pipeline.py
Full multi-agent pipeline — all 4 agents running in sequence.

Shows state at each stage so you can see what each agent contributes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from state import ResearchState
from agents.researcher import ResearcherAgent
from agents.analyzer   import AnalyzerAgent
from agents.critic     import CriticAgent
from agents.writer     import WriterAgent


def preview(text: str, chars: int = 300) -> str:
    """Return first N chars of text with ellipsis if truncated."""
    if len(text) <= chars:
        return text
    return text[:chars].rstrip() + "..."


def run_pipeline(topic: str):
    print(f"\n{'='*60}")
    print(f"  Full Pipeline Run")
    print(f"  Topic: {topic}")
    print(f"{'='*60}")

    state = ResearchState(topic=topic)

    # ── Stage 1: Researcher ───────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("  STAGE 1 — Researcher Agent")
    print(f"{'─'*60}")
    print("  Searching the web...\n")

    researcher = ResearcherAgent()
    state = researcher.run(state)

    print(f"\n  Results: {len(state.search_results)} sources found")
    for i, r in enumerate(state.search_results[:4], 1):
        print(f"  {i}. {r['title'][:70]}")
    if len(state.search_results) > 4:
        print(f"  ... and {len(state.search_results) - 4} more")

    # ── Stage 2: Analyzer ─────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("  STAGE 2 — Analyzer Agent")
    print(f"{'─'*60}")
    print("  Analyzing search results...\n")

    analyzer = AnalyzerAgent()
    state = analyzer.run(state)

    print(f"\n  Analysis preview:")
    print("  " + preview(state.analysis).replace("\n", "\n  "))

    # ── Stage 3: Critic ───────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("  STAGE 3 — Critic Agent")
    print(f"{'─'*60}")
    print("  Reviewing the analysis...\n")

    critic = CriticAgent()
    state = critic.run(state)

    print(f"\n  Critique preview:")
    print("  " + preview(state.critique).replace("\n", "\n  "))

    # ── Stage 4: Writer ───────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("  STAGE 4 — Writer Agent")
    print(f"{'─'*60}")
    print("  Writing the final report...\n")

    writer = WriterAgent()
    state = writer.run(state)

    # ── Final output ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  FINAL REPORT")
    print(f"{'='*60}\n")
    print(state.final_report)

    print(f"\n{'='*60}")
    print(f"  Pipeline complete. Status: {state.status}")
    print(f"  Sources: {len(state.search_results)}  |  Report: {len(state.final_report)} chars")
    print(f"{'='*60}\n")

    return state


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "renewable energy trends in 2024"
    run_pipeline(topic)
