"""
01_individual_agents.py
Test each agent individually — using real web search data throughout.

Each agent runs in sequence so every agent gets real inputs:
  Researcher  → real web search results
  Analyzer    → real analysis of those results
  Critic      → real critique of that analysis
  Writer      → real report from analysis + critique

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


TOPIC = "impact of artificial intelligence on healthcare"


def separator(title: str):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}\n")


# ── Test 1: Researcher Agent ───────────────────────────────────────────────────

def test_researcher(state: ResearchState) -> ResearchState:
    separator("TEST 1: Researcher Agent")
    print(f"Topic: {state.topic}")
    print("Running web searches via function calling...\n")

    agent = ResearcherAgent()
    state = agent.run(state)

    print(f"\nResults collected: {len(state.search_results)}")
    for i, r in enumerate(state.search_results, 1):
        print(f"  {i}. {r['title']}")
        print(f"     {r['url']}")

    return state


# ── Test 2: Analyzer Agent ────────────────────────────────────────────────────

def test_analyzer(state: ResearchState) -> ResearchState:
    separator("TEST 2: Analyzer Agent")
    print(f"Analyzing {len(state.search_results)} real search results...\n")

    agent = AnalyzerAgent()
    state = agent.run(state)

    print("\nAnalysis output:")
    print(state.analysis)

    return state


# ── Test 3: Critic Agent ──────────────────────────────────────────────────────

def test_critic(state: ResearchState) -> ResearchState:
    separator("TEST 3: Critic Agent")
    print("Critiquing the real analysis...\n")

    agent = CriticAgent()
    state = agent.run(state)

    print("\nCritique output:")
    print(state.critique)

    return state


# ── Test 4: Writer Agent ──────────────────────────────────────────────────────

def test_writer(state: ResearchState) -> ResearchState:
    separator("TEST 4: Writer Agent")
    print("Writing final report from real analysis + critique...\n")

    agent = WriterAgent()
    state = agent.run(state)

    print("\nFinal report:")
    print(state.final_report)

    return state


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Individual Agent Tests")
    print(f"  Topic: {TOPIC}")
    print("=" * 55)
    print("\nEach agent runs with real data from the previous step.\n")

    state = ResearchState(topic=TOPIC)

    state = test_researcher(state)
    state = test_analyzer(state)
    state = test_critic(state)
    state = test_writer(state)

    print("\n" + "=" * 55)
    print("  All individual agent tests complete.")
    print("=" * 55)
