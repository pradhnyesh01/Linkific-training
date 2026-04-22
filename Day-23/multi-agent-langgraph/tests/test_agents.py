"""
tests/test_agents.py
Tests for individual agents — all LLM calls are mocked.

Focuses on:
- CriticAgent: routing decision parsing (the key Day-23 addition)
- AnalyzerAgent: handles empty results gracefully
- WriterAgent: handles empty analysis gracefully
- ResearcherAgent: deduplicates results by URL
"""

import pytest
from unittest.mock import patch, MagicMock
from conftest import MockState


# ── CriticAgent ───────────────────────────────────────────────────────────────

class TestCriticAgent:

    def _run_critic(self, mock_response: str, analysis: str = "Some analysis text.", iteration: int = 1):
        """Helper: run CriticAgent with a mocked _chat response."""
        from agents.critic import CriticAgent
        agent = CriticAgent()
        state = MockState(topic="AI", analysis=analysis, iteration=iteration)
        with patch.object(agent, "_chat", return_value=mock_response):
            agent.run(state)
        return state

    def test_parses_approved_routing(self):
        state = self._run_critic("Good analysis.\nROUTING: approved")
        assert state.routing_decision == "approved"

    def test_parses_needs_more_research_routing(self):
        state = self._run_critic("Missing stats.\nROUTING: needs_more_research")
        assert state.routing_decision == "needs_more_research"

    def test_routing_line_stripped_from_critique(self):
        state = self._run_critic("Good work.\nROUTING: approved")
        assert "ROUTING:" not in state.critique

    def test_critique_text_preserved(self):
        state = self._run_critic("The analysis is comprehensive.\nROUTING: approved")
        assert "comprehensive" in state.critique

    def test_defaults_to_approved_when_routing_line_missing(self):
        state = self._run_critic("The analysis looks okay. No routing line here.")
        assert state.routing_decision == "approved"

    def test_defaults_to_approved_on_invalid_routing_value(self):
        state = self._run_critic("Good.\nROUTING: maybe")
        assert state.routing_decision == "approved"

    def test_handles_empty_analysis_gracefully(self):
        state = self._run_critic("", analysis="")
        assert state.critique         == "No analysis available to critique."
        assert state.routing_decision == "approved"

    def test_routing_case_insensitive(self):
        state = self._run_critic("Good.\nROUTING: Approved")
        assert state.routing_decision == "approved"

    def test_routing_parsed_from_last_matching_line(self):
        """If ROUTING appears multiple times, last one wins."""
        response = "ROUTING: needs_more_research\nMore text.\nROUTING: approved"
        state = self._run_critic(response)
        assert state.routing_decision == "approved"

    def test_log_entry_added(self):
        state = self._run_critic("Analysis done.\nROUTING: approved")
        assert len(state._log) >= 1


# ── AnalyzerAgent ─────────────────────────────────────────────────────────────

class TestAnalyzerAgent:

    def _run_analyzer(self, search_results, mock_response="Detailed analysis."):
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent()
        state = MockState(topic="AI", search_results=search_results)
        with patch.object(agent, "_chat", return_value=mock_response):
            agent.run(state)
        return state

    def test_writes_analysis_to_state(self, sample_search_results):
        state = self._run_analyzer(sample_search_results)
        assert state.analysis == "Detailed analysis."

    def test_handles_empty_search_results(self):
        state = self._run_analyzer([])
        assert state.analysis == "No search results available to analyze."

    def test_log_entry_added(self, sample_search_results):
        state = self._run_analyzer(sample_search_results)
        assert len(state._log) >= 1


# ── WriterAgent ───────────────────────────────────────────────────────────────

class TestWriterAgent:

    def _run_writer(self, analysis="Some analysis.", critique="Some critique.", mock_response="# Final Report\nContent."):
        from agents.writer import WriterAgent
        agent = WriterAgent()
        state = MockState(topic="AI", analysis=analysis, critique=critique)
        with patch.object(agent, "_chat", return_value=mock_response):
            agent.run(state)
        return state

    def test_writes_final_report(self):
        state = self._run_writer()
        assert state.final_report == "# Final Report\nContent."

    def test_handles_empty_analysis(self):
        state = self._run_writer(analysis="")
        assert "Insufficient" in state.final_report

    def test_report_includes_topic_on_empty_analysis(self):
        state = self._run_writer(analysis="")
        assert "AI" in state.final_report  # topic should appear

    def test_log_entry_added(self):
        state = self._run_writer()
        assert len(state._log) >= 1


# ── ResearcherAgent ───────────────────────────────────────────────────────────

class TestResearcherAgent:

    def test_deduplicates_results_by_url(self):
        """Two searches returning the same URL should yield one result."""
        from agents.researcher import ResearcherAgent

        duplicate_result = {"title": "AI Article", "url": "https://example.com/1", "snippet": "snippet"}
        tool_calls = [
            {"name": "web_search", "args": {"query": "AI"}, "result": {
                "success": True, "results": [duplicate_result],
            }},
            {"name": "web_search", "args": {"query": "AI healthcare"}, "result": {
                "success": True, "results": [duplicate_result],   # same URL
            }},
        ]

        agent = ResearcherAgent()
        state = MockState(topic="AI")
        with patch.object(agent, "_chat_with_tools", return_value=("Done.", tool_calls)):
            agent.run(state)

        assert len(state.search_results) == 1

    def test_failed_search_not_added(self):
        """Results from a failed tool call should be ignored."""
        from agents.researcher import ResearcherAgent

        tool_calls = [
            {"name": "web_search", "args": {"query": "AI"}, "result": {
                "success": False, "error": "rate limit",
            }},
        ]

        agent = ResearcherAgent()
        state = MockState(topic="AI")
        with patch.object(agent, "_chat_with_tools", return_value=("Done.", tool_calls)):
            agent.run(state)

        assert state.search_results == []

    def test_collects_results_from_multiple_searches(self):
        """Results from multiple tool calls should all be collected."""
        from agents.researcher import ResearcherAgent

        tool_calls = [
            {"name": "web_search", "args": {}, "result": {
                "success": True,
                "results": [
                    {"title": "A", "url": "https://a.com", "snippet": "a"},
                ],
            }},
            {"name": "web_search", "args": {}, "result": {
                "success": True,
                "results": [
                    {"title": "B", "url": "https://b.com", "snippet": "b"},
                ],
            }},
        ]

        agent = ResearcherAgent()
        state = MockState(topic="AI")
        with patch.object(agent, "_chat_with_tools", return_value=("Done.", tool_calls)):
            agent.run(state)

        assert len(state.search_results) == 2
