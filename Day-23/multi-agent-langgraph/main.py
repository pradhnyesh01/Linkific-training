"""
main.py
Entry point for the Day-23 LangGraph multi-agent research system.

Uses stream(stream_mode="values") so you see the full state after
each node completes — no waiting until the very end.

Usage:
    python main.py
    python main.py "your custom topic here"
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from graph import research_graph
from cost_tracker import tracker
from logger import get_logger

log = get_logger("main")

DEFAULT_TOPIC = "impact of artificial intelligence on healthcare"

# Tracks which node just ran (for printing headers once per node)
_SEEN_NODES = {
    "pending":     None,
    "researching": "Researcher",
    "analyzing":   "Analyzer",
    "critiquing":  "Critic",
    "writing":     "Writer",
    "done":        None,
}


def run(topic: str) -> dict:
    """
    Run the full research pipeline via LangGraph with real-time output.

    stream_mode="values" yields the FULL accumulated state after each
    node completes — so you see progress at every step.

    Args:
        topic: Research question or topic.

    Returns:
        Final ResearchState dict with all fields populated.
    """
    log.info(f"Pipeline started — topic: {topic}")
    tracker.reset()

    print(f"\n{'='*60}", flush=True)
    print(f"  Multi-Agent Research System (LangGraph)", flush=True)
    print(f"  Topic: {topic}", flush=True)
    print(f"{'='*60}\n", flush=True)

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

    final_state  = None
    last_status  = "pending"

    # stream_mode="values" → yields full state after every node
    for state in research_graph.stream(initial_state, stream_mode="values"):
        current_status = state.get("status", "pending")

        # Print a section header whenever the pipeline moves to a new stage
        if current_status != last_status:
            node_label = _SEEN_NODES.get(current_status)
            if node_label:
                print(f"\n{'─'*60}", flush=True)
                print(f"  ✓ {node_label} complete", flush=True)

                # Show a short summary of what this node produced
                if current_status == "researching":
                    n = len(state.get("search_results", []))
                    print(f"    Sources found   : {n}", flush=True)

                elif current_status == "analyzing":
                    analysis = state.get("analysis", "")
                    preview  = analysis[:120].replace("\n", " ")
                    print(f"    Analysis preview: {preview}...", flush=True)

                elif current_status == "critiquing":
                    routing  = state.get("routing_decision", "?")
                    critique = state.get("critique", "")
                    preview  = critique[:120].replace("\n", " ")
                    print(f"    Routing decision: {routing}", flush=True)
                    print(f"    Critique preview: {preview}...", flush=True)

                elif current_status == "done":
                    report = state.get("final_report", "")
                    print(f"    Report length   : {len(report)} chars", flush=True)

            last_status = current_status

        final_state = state

    # ── Final report ───────────────────────────────────────────────────────────
    print(f"\n{'='*60}", flush=True)
    print("  FINAL REPORT", flush=True)
    print(f"{'='*60}\n", flush=True)
    print(final_state["final_report"], flush=True)

    # ── Pipeline summary ───────────────────────────────────────────────────────
    print(f"\n{'='*60}", flush=True)
    print("  PIPELINE SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"  Research iterations : {final_state['iteration']}", flush=True)
    print(f"  Sources collected   : {len(final_state['search_results'])}", flush=True)
    print(f"  Routing decision    : {final_state['routing_decision']}", flush=True)
    print(f"  Final status        : {final_state['status']}", flush=True)
    print(f"\n  Agent log:", flush=True)
    for entry in final_state["log"]:
        print(f"    {entry}", flush=True)

    tracker.summary()
    log.info("Pipeline complete")
    return final_state


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_TOPIC
    run(topic)
