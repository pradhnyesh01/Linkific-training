"""
01_simple_query.py
Tests the pipeline with a simple, well-defined factual topic.

Simple queries typically get approved by the Critic in one pass
(no looping back to Researcher). Good for verifying the happy path.

Run from Day-23/multi-agent-langgraph/:
    python examples/01_simple_query.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from main import run

if __name__ == "__main__":
    topic = "how does photosynthesis work"

    print("Simple factual query — expect 1 research iteration, Critic approves.\n", flush=True)
    state = run(topic)

    print(f"\nIterations used : {state['iteration']} / 2")
    print(f"Routing         : {state['routing_decision']}")
