"""
state.py
Shared state for the LangGraph multi-agent pipeline.

Uses TypedDict (required by LangGraph) instead of Day-22's dataclass.

Annotated[list, operator.add] tells LangGraph to APPEND to the list
across graph steps instead of replacing it. Used for:
  - search_results  : new searches add to existing ones during re-research loops
  - log             : every agent's log entries accumulate across the full run

All other fields (strings, int) are replaced on each update.
"""

from typing import TypedDict, Annotated
import operator


class ResearchState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────────────
    topic:            str

    # ── Agent outputs (populated as pipeline progresses) ──────────────────────
    search_results:   Annotated[list[dict], operator.add]   # Researcher
    analysis:         str                                    # Analyzer
    critique:         str                                    # Critic
    routing_decision: str                                    # Critic → "approved" | "needs_more_research"
    final_report:     str                                    # Writer

    # ── Control flow ──────────────────────────────────────────────────────────
    iteration:        int          # how many times Researcher has run (max 2)
    status:           str          # pending → researching → analyzing → critiquing → writing → done
    log:              Annotated[list[str], operator.add]    # one line per agent action
