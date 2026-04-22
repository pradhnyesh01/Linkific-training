"""
tests/test_graph.py
Tests for graph.py — StateAdapter and routing logic.

No LLM calls, no web searches. Pure logic tests.
"""

import pytest
from graph import StateAdapter, route_after_critic


# ── StateAdapter ──────────────────────────────────────────────────────────────

class TestStateAdapter:

    def test_reads_topic(self, empty_state):
        adapter = StateAdapter(empty_state)
        assert adapter.topic == "artificial intelligence in healthcare"

    def test_reads_search_results(self, state_after_research, sample_search_results):
        adapter = StateAdapter(state_after_research)
        assert adapter.search_results == sample_search_results

    def test_reads_analysis(self, state_after_analysis):
        adapter = StateAdapter(state_after_analysis)
        assert adapter.analysis != ""

    def test_reads_iteration(self, state_after_research):
        adapter = StateAdapter(state_after_research)
        assert adapter.iteration == 1

    def test_defaults_on_empty_state(self):
        adapter = StateAdapter({"topic": "test"})
        assert adapter.search_results   == []
        assert adapter.analysis         == ""
        assert adapter.critique         == ""
        assert adapter.routing_decision == ""
        assert adapter.final_report     == ""
        assert adapter.status           == "pending"
        assert adapter.iteration        == 0

    def test_add_log_appends_entry(self, empty_state):
        adapter = StateAdapter(empty_state)
        adapter.add_log("Researcher", "Found 5 results")
        assert len(adapter._log) == 1
        assert "[Researcher] Found 5 results" in adapter._log[0]

    def test_add_log_multiple_entries(self, empty_state):
        adapter = StateAdapter(empty_state)
        adapter.add_log("Researcher", "Searching...")
        adapter.add_log("Researcher", "Done.")
        assert len(adapter._log) == 2

    def test_log_starts_empty(self, empty_state):
        adapter = StateAdapter(empty_state)
        assert adapter._log == []

    def test_search_results_is_a_copy(self, state_after_research):
        """Modifying adapter.search_results should not affect original state."""
        adapter = StateAdapter(state_after_research)
        adapter.search_results.append({"title": "Extra", "url": "x", "snippet": "x"})
        assert len(state_after_research["search_results"]) == 3  # unchanged


# ── route_after_critic() ──────────────────────────────────────────────────────

class TestRouteAfterCritic:

    def test_approved_routes_to_writer(self):
        state = {"routing_decision": "approved", "iteration": 1}
        assert route_after_critic(state) == "writer"

    def test_needs_more_research_under_limit_routes_to_researcher(self):
        state = {"routing_decision": "needs_more_research", "iteration": 1}
        assert route_after_critic(state) == "researcher"

    def test_needs_more_research_at_limit_routes_to_writer(self):
        state = {"routing_decision": "needs_more_research", "iteration": 2}
        assert route_after_critic(state) == "writer"

    def test_needs_more_research_above_limit_routes_to_writer(self):
        state = {"routing_decision": "needs_more_research", "iteration": 5}
        assert route_after_critic(state) == "writer"

    def test_approved_at_limit_still_routes_to_writer(self):
        state = {"routing_decision": "approved", "iteration": 2}
        assert route_after_critic(state) == "writer"

    def test_missing_routing_decision_defaults_to_writer(self):
        """Empty string routing_decision should not route to researcher."""
        state = {"routing_decision": "", "iteration": 1}
        assert route_after_critic(state) == "writer"

    def test_iteration_zero_with_needs_more_research(self):
        """Even at iteration 0, needs_more_research should loop (< 2)."""
        state = {"routing_decision": "needs_more_research", "iteration": 0}
        assert route_after_critic(state) == "researcher"

    def test_iteration_boundary_exactly_2(self):
        """iteration == 2 is the cap — must go to writer."""
        state = {"routing_decision": "needs_more_research", "iteration": 2}
        assert route_after_critic(state) == "writer"

    def test_iteration_boundary_exactly_1(self):
        """iteration == 1 is under cap — can still loop."""
        state = {"routing_decision": "needs_more_research", "iteration": 1}
        assert route_after_critic(state) == "researcher"
