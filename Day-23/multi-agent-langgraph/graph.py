"""
graph.py
LangGraph StateGraph — wires all agents into a conditional workflow.

Pipeline:
  START → Researcher → Analyzer → Critic
                                     │
                          ┌──────────┴──────────┐
                          │ needs_more_research  │ approved
                          │  (max 2 iterations)  │
                          ↓                      ↓
                       Researcher             Writer → END

Key concepts used:
  StateGraph        — defines the graph structure
  add_node()        — registers each agent as a node
  add_edge()        — fixed transition between nodes
  add_conditional_edges() — Critic's output decides next node
  StateAdapter      — bridges LangGraph's TypedDict ↔ Day-22 agent interface
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from langgraph.graph import StateGraph, END

from state import ResearchState
from agents.researcher import ResearcherAgent
from agents.analyzer   import AnalyzerAgent
from agents.critic     import CriticAgent
from agents.writer     import WriterAgent


# ── State Adapter ──────────────────────────────────────────────────────────────

class StateAdapter:
    """
    Bridges LangGraph's TypedDict state and the Day-22 agent interface.

    Day-22 agents use attribute access (state.topic, state.analysis).
    LangGraph uses dict access (state["topic"], state["analysis"]).

    This adapter wraps the dict and exposes it as attributes so all
    Day-22 agents work inside LangGraph without modification.
    """

    def __init__(self, state: dict):
        self.topic            = state.get("topic", "")
        self.search_results   = list(state.get("search_results", []))
        self.analysis         = state.get("analysis", "")
        self.critique         = state.get("critique", "")
        self.routing_decision = state.get("routing_decision", "")
        self.final_report     = state.get("final_report", "")
        self.status           = state.get("status", "pending")
        self.iteration        = state.get("iteration", 0)
        self._log             = []

    def add_log(self, agent_name: str, message: str):
        entry = f"[{agent_name}] {message}"
        self._log.append(entry)
        print(entry, flush=True)

    def as_update(self, include_search: bool = True) -> dict:
        """Returns only the fields that changed — passed back to LangGraph."""
        update = {
            "analysis":         self.analysis,
            "critique":         self.critique,
            "routing_decision": self.routing_decision,
            "final_report":     self.final_report,
            "status":           self.status,
            "log":              self._log,
        }
        if include_search:
            update["search_results"] = self.search_results
        return update


# ── Node functions (one per agent) ────────────────────────────────────────────

def researcher_node(state: ResearchState) -> dict:
    """Run the Researcher agent and return new search results."""
    adapter = StateAdapter(state)
    adapter.search_results = []   # start fresh; LangGraph will append via operator.add

    agent = ResearcherAgent()
    agent.run(adapter)

    return {
        "search_results": adapter.search_results,
        "iteration":      state.get("iteration", 0) + 1,
        "status":         "researching",
        "log":            adapter._log,
    }


def analyzer_node(state: ResearchState) -> dict:
    """Run the Analyzer agent over all accumulated search results."""
    adapter = StateAdapter(state)

    agent = AnalyzerAgent()
    agent.run(adapter)

    return {
        "analysis": adapter.analysis,
        "status":   "analyzing",
        "log":      adapter._log,
    }


def critic_node(state: ResearchState) -> dict:
    """Run the Critic agent and capture the routing decision."""
    adapter = StateAdapter(state)

    agent = CriticAgent()
    agent.run(adapter)

    return {
        "critique":         adapter.critique,
        "routing_decision": adapter.routing_decision,
        "status":           "critiquing",
        "log":              adapter._log,
    }


def writer_node(state: ResearchState) -> dict:
    """Run the Writer agent to produce the final report."""
    adapter = StateAdapter(state)

    agent = WriterAgent()
    agent.run(adapter)

    return {
        "final_report": adapter.final_report,
        "status":       "done",
        "log":          adapter._log,
    }


# ── Routing logic ──────────────────────────────────────────────────────────────

def route_after_critic(state: ResearchState) -> str:
    """
    After the Critic runs, decide the next node.

    Rules:
      - If Critic says "needs_more_research" AND iteration < 2 → researcher
      - Otherwise (approved OR max iterations reached)          → writer

    Max 2 research iterations prevents infinite loops.
    """
    decision  = state.get("routing_decision", "approved")
    iteration = state.get("iteration", 0)

    if decision == "needs_more_research" and iteration < 2:
        print(f"\n[Coordinator] Critic requested more research "
              f"(iteration {iteration}/2). Looping back to Researcher.\n", flush=True)
        return "researcher"

    if iteration >= 2 and decision == "needs_more_research":
        print(f"\n[Coordinator] Max iterations reached ({iteration}). "
              f"Proceeding to Writer despite critique.\n", flush=True)

    return "writer"


# ── Graph builder ──────────────────────────────────────────────────────────────

def build_graph():
    """
    Constructs and compiles the LangGraph StateGraph.

    Returns a compiled graph ready to invoke with:
        graph.invoke({"topic": "your topic", ...})
    """
    graph = StateGraph(ResearchState)

    # Register nodes
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyzer",   analyzer_node)
    graph.add_node("critic",     critic_node)
    graph.add_node("writer",     writer_node)

    # Fixed edges
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "analyzer")
    graph.add_edge("analyzer",   "critic")
    graph.add_edge("writer",     END)

    # Conditional edge from Critic
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "researcher": "researcher",   # needs_more_research → loop
            "writer":     "writer",       # approved → finalize
        },
    )

    return graph.compile()


# ── Pre-built graph instance (import and use directly) ────────────────────────

research_graph = build_graph()
