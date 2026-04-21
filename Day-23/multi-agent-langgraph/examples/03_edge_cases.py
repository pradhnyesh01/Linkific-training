"""
03_edge_cases.py
Tests edge cases and error scenarios.

Cases covered:
  1. Very short/vague topic     — system should still produce a report
  2. Very narrow niche topic    — limited search results, tests graceful handling
  3. Max iteration enforcement  — verifies pipeline doesn't loop more than twice

Run from Day-23/multi-agent-langgraph/:
    python examples/03_edge_cases.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from graph import research_graph


def run_case(label: str, topic: str):
    print(f"\n{'='*60}")
    print(f"  CASE: {label}")
    print(f"  Topic: {topic}")
    print(f"{'='*60}\n")

    initial_state = {
        "topic":            topic,
        "search_results":   [],
        "analysis":         "",
        "critique":         "",
        "routing_decision": "",
        "final_report":     "",
        "iteration":        0,
        "status":           "pending",
        "log":              [],
    }

    try:
        state = research_graph.invoke(initial_state)
        print(f"\n  Result:")
        print(f"  Status     : {state['status']}")
        print(f"  Iterations : {state['iteration']}")
        print(f"  Sources    : {len(state['search_results'])}")
        print(f"  Routing    : {state['routing_decision']}")
        print(f"  Report len : {len(state['final_report'])} chars")
        print(f"  Report preview: {state['final_report'][:200]}...")
        return state

    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}")
        return None


if __name__ == "__main__":
    # Case 1: Very vague/short topic
    run_case(
        label = "Vague topic",
        topic = "technology",
    )

    # Case 2: Narrow niche topic
    run_case(
        label = "Narrow niche",
        topic = "the history of left-handed medieval swordsmanship techniques",
    )

    # Case 3: Max iteration enforcement
    # Simulate a state where iteration is already at 2 to verify
    # the pipeline stops looping and routes to writer regardless
    print(f"\n{'='*60}")
    print("  CASE: Max iteration guard test")
    print(f"{'='*60}\n")
    print("  Pre-loading state with iteration=2 and routing_decision=needs_more_research")
    print("  Expected: pipeline should route to Writer, not loop again.\n")

    forced_state = {
        "topic":            "test topic",
        "search_results":   [{"title": "Test", "url": "http://test.com", "snippet": "Test data"}],
        "analysis":         "This is a test analysis with some content.",
        "critique":         "",
        "routing_decision": "needs_more_research",
        "final_report":     "",
        "iteration":        2,     # already at max
        "status":           "critiquing",
        "log":              [],
    }

    from graph import critic_node, route_after_critic
    critique_update = critic_node(forced_state)
    forced_state.update(critique_update)

    next_node = route_after_critic(forced_state)
    print(f"  routing_decision : {forced_state.get('routing_decision')}")
    print(f"  next_node        : {next_node}")
    assert next_node == "writer", f"Expected 'writer' but got '{next_node}'"
    print("  ✓ Max iteration guard works correctly — routed to Writer.")
