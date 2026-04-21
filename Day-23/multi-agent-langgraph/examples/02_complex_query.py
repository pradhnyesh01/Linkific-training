"""
02_complex_query.py
Tests the pipeline with a broad, multi-faceted research topic.

Complex queries are more likely to trigger the Critic's
"needs_more_research" decision, causing the pipeline to loop
back to the Researcher for a second round of searches.

Run from Day-23/multi-agent-langgraph/:
    python examples/02_complex_query.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from main import run

if __name__ == "__main__":
    topic = "geopolitical and economic impact of the global semiconductor shortage"

    print("Complex multi-faceted query — Critic may request additional research.\n")
    state = run(topic)

    print(f"\nIterations used  : {state['iteration']} / 2")
    print(f"Routing decision : {state['routing_decision']}")
    print(f"Total sources    : {len(state['search_results'])}")

    if state["iteration"] > 1:
        print("\n→ Critic sent the pipeline back for more research (loop triggered).")
    else:
        print("\n→ Critic approved after first research pass.")
