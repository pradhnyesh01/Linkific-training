"""
main.py
Entry point — runs the full multi-agent research pipeline.

Usage:
    python main.py
    python main.py "your custom topic here"

The pipeline runs:
  Researcher → Analyzer → Critic → Writer

Output: a formatted markdown research report printed to terminal.
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from agents.coordinator import CoordinatorAgent

DEFAULT_TOPIC = "impact of artificial intelligence on healthcare"

def main():
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_TOPIC

    coordinator = CoordinatorAgent()
    state = coordinator.run(topic)

    print("\n" + "=" * 60)
    print("  FINAL REPORT")
    print("=" * 60 + "\n")
    print(state.final_report)

if __name__ == "__main__":
    main()
