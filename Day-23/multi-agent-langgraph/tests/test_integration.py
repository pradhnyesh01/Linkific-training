"""
tests/test_integration.py
Integration tests — runs the full LangGraph pipeline with mocked agents.

All LLM and web search calls are mocked so:
- Tests run fast (no API calls)
- Tests are free (no token cost)
- Tests are deterministic (no random LLM responses)

Verifies:
- Full pipeline produces a final_report
- State fields are populated correctly at each stage
- Routing logic integrates correctly with the graph
- Re-research loop triggers and terminates
"""

import pytest
from unittest.mock import patch, MagicMock
from graph import research_graph, StateAdapter, route_after_critic


# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_SEARCH_RESULTS = [
    {"title": "AI Healthcare Study", "url": "https://example.com/1", "snippet": "AI improves diagnostics."},
    {"title": "ML Drug Discovery",   "url": "https://example.com/2", "snippet": "ML accelerates research."},
]

MOCK_ANALYSIS  = "AI is transforming healthcare through diagnostics and drug discovery."
MOCK_CRITIQUE  = "Good overview but lacks regulatory context.\nROUTING: approved"
MOCK_REPORT    = "# AI in Healthcare\n\n## Summary\nAI is revolutionising healthcare."


def make_node_mocks():
    """Returns patch targets and side effects for all 4 node functions."""
    def mock_researcher(state):
        return {
            "search_results": MOCK_SEARCH_RESULTS,
            "iteration":      state.get("iteration", 0) + 1,
            "status":         "researching",
            "log":            ["[Researcher] Found 2 results"],
        }

    def mock_analyzer(state):
        return {
            "analysis": MOCK_ANALYSIS,
            "status":   "analyzing",
            "log":      ["[Analyzer] Analysis complete"],
        }

    def mock_critic_approved(state):
        return {
            "critique":         "Good analysis.",
            "routing_decision": "approved",
            "status":           "critiquing",
            "log":              ["[Critic] Routing: approved"],
        }

    def mock_writer(state):
        return {
            "final_report": MOCK_REPORT,
            "status":       "done",
            "log":          ["[Writer] Report complete"],
        }

    return mock_researcher, mock_analyzer, mock_critic_approved, mock_writer


# ── Happy path ────────────────────────────────────────────────────────────────

class TestFullPipelineApproved:
    """Pipeline where Critic approves on first pass — no looping."""

    def setup_method(self):
        self.initial = {
            "topic":            "AI in healthcare",
            "search_results":   [],
            "analysis":         "",
            "critique":         "",
            "routing_decision": "",
            "final_report":     "",
            "iteration":        0,
            "status":           "pending",
            "log":              [],
        }

    def test_final_report_is_populated(self):
        r, a, c, w = make_node_mocks()
        with patch("graph.researcher_node", side_effect=r), \
             patch("graph.analyzer_node",   side_effect=a), \
             patch("graph.critic_node",     side_effect=c), \
             patch("graph.writer_node",     side_effect=w):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)
        assert state["final_report"] == MOCK_REPORT

    def test_status_is_done(self):
        r, a, c, w = make_node_mocks()
        with patch("graph.researcher_node", side_effect=r), \
             patch("graph.analyzer_node",   side_effect=a), \
             patch("graph.critic_node",     side_effect=c), \
             patch("graph.writer_node",     side_effect=w):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)
        assert state["status"] == "done"

    def test_search_results_accumulated(self):
        r, a, c, w = make_node_mocks()
        with patch("graph.researcher_node", side_effect=r), \
             patch("graph.analyzer_node",   side_effect=a), \
             patch("graph.critic_node",     side_effect=c), \
             patch("graph.writer_node",     side_effect=w):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)
        assert len(state["search_results"]) == 2

    def test_iteration_incremented(self):
        r, a, c, w = make_node_mocks()
        with patch("graph.researcher_node", side_effect=r), \
             patch("graph.analyzer_node",   side_effect=a), \
             patch("graph.critic_node",     side_effect=c), \
             patch("graph.writer_node",     side_effect=w):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)
        assert state["iteration"] == 1

    def test_log_contains_all_agent_entries(self):
        r, a, c, w = make_node_mocks()
        with patch("graph.researcher_node", side_effect=r), \
             patch("graph.analyzer_node",   side_effect=a), \
             patch("graph.critic_node",     side_effect=c), \
             patch("graph.writer_node",     side_effect=w):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)
        log_text = " ".join(state["log"])
        assert "Researcher" in log_text
        assert "Analyzer"   in log_text
        assert "Critic"     in log_text
        assert "Writer"     in log_text


# ── Re-research loop ──────────────────────────────────────────────────────────

class TestReResearchLoop:
    """Pipeline where Critic requests more research on first pass."""

    def setup_method(self):
        self.initial = {
            "topic":            "AI in healthcare",
            "search_results":   [],
            "analysis":         "",
            "critique":         "",
            "routing_decision": "",
            "final_report":     "",
            "iteration":        0,
            "status":           "pending",
            "log":              [],
        }
        self.call_count = {"critic": 0}

    def test_loop_runs_researcher_twice(self):
        researcher_calls = []

        def mock_researcher(state):
            researcher_calls.append(1)
            return {
                "search_results": MOCK_SEARCH_RESULTS,
                "iteration":      state.get("iteration", 0) + 1,
                "status":         "researching",
                "log":            [],
            }

        critic_calls = [0]

        def mock_critic(state):
            critic_calls[0] += 1
            # First call: reject. Second call: approve.
            decision = "needs_more_research" if critic_calls[0] == 1 else "approved"
            return {
                "critique":         f"Call {critic_calls[0]}.",
                "routing_decision": decision,
                "status":           "critiquing",
                "log":              [],
            }

        with patch("graph.researcher_node", side_effect=mock_researcher), \
             patch("graph.analyzer_node",   side_effect=lambda s: {"analysis": MOCK_ANALYSIS, "status": "analyzing", "log": []}), \
             patch("graph.critic_node",     side_effect=mock_critic), \
             patch("graph.writer_node",     side_effect=lambda s: {"final_report": MOCK_REPORT, "status": "done", "log": []}):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)

        assert len(researcher_calls) == 2
        assert state["iteration"] == 2

    def test_max_iteration_guard_stops_loop(self):
        """Even if Critic always rejects, pipeline stops at iteration 2."""
        researcher_calls = []

        def mock_researcher(state):
            researcher_calls.append(1)
            return {
                "search_results": MOCK_SEARCH_RESULTS,
                "iteration":      state.get("iteration", 0) + 1,
                "status":         "researching",
                "log":            [],
            }

        def mock_critic_always_rejects(state):
            return {
                "critique":         "Always needs more.",
                "routing_decision": "needs_more_research",
                "status":           "critiquing",
                "log":              [],
            }

        with patch("graph.researcher_node", side_effect=mock_researcher), \
             patch("graph.analyzer_node",   side_effect=lambda s: {"analysis": MOCK_ANALYSIS, "status": "analyzing", "log": []}), \
             patch("graph.critic_node",     side_effect=mock_critic_always_rejects), \
             patch("graph.writer_node",     side_effect=lambda s: {"final_report": MOCK_REPORT, "status": "done", "log": []}):
            graph = __import__("graph").build_graph()
            state = graph.invoke(self.initial)

        # Should have run Researcher exactly twice (iteration cap = 2)
        assert len(researcher_calls) == 2
        assert state["final_report"] == MOCK_REPORT
