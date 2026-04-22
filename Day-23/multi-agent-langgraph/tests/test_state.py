"""
tests/test_state.py
Tests for the ResearchState TypedDict structure.

Verifies:
- All required keys are present
- Annotated[list, operator.add] accumulation works correctly
- Default values are correct types
"""

import operator
import pytest
from state import ResearchState


class TestResearchStateStructure:
    """Verify the TypedDict has all expected keys with correct types."""

    def test_required_keys_present(self, empty_state):
        required = [
            "topic", "search_results", "analysis", "critique",
            "routing_decision", "final_report", "iteration", "status", "log",
        ]
        for key in required:
            assert key in empty_state, f"Missing key: {key}"

    def test_default_types(self, empty_state):
        assert isinstance(empty_state["topic"],            str)
        assert isinstance(empty_state["search_results"],   list)
        assert isinstance(empty_state["analysis"],         str)
        assert isinstance(empty_state["critique"],         str)
        assert isinstance(empty_state["routing_decision"], str)
        assert isinstance(empty_state["final_report"],     str)
        assert isinstance(empty_state["iteration"],        int)
        assert isinstance(empty_state["status"],           str)
        assert isinstance(empty_state["log"],              list)

    def test_initial_values(self, empty_state):
        assert empty_state["topic"]            == "artificial intelligence in healthcare"
        assert empty_state["search_results"]   == []
        assert empty_state["analysis"]         == ""
        assert empty_state["iteration"]        == 0
        assert empty_state["status"]           == "pending"
        assert empty_state["log"]              == []


class TestAnnotatedListAccumulation:
    """
    Verify operator.add behaviour — LangGraph uses this to merge
    list fields across graph steps instead of replacing them.
    """

    def test_operator_add_merges_lists(self):
        existing = [{"title": "A", "url": "http://a.com", "snippet": "a"}]
        new      = [{"title": "B", "url": "http://b.com", "snippet": "b"}]
        merged   = operator.add(existing, new)
        assert len(merged) == 2
        assert merged[0]["title"] == "A"
        assert merged[1]["title"] == "B"

    def test_operator_add_on_empty_list(self):
        result = operator.add([], [{"title": "X"}])
        assert len(result) == 1

    def test_operator_add_idempotent_with_empty(self):
        existing = [{"title": "A"}]
        result   = operator.add(existing, [])
        assert result == existing

    def test_log_accumulation(self):
        log1 = ["[Researcher] done"]
        log2 = ["[Analyzer] done"]
        merged = operator.add(log1, log2)
        assert len(merged) == 2
        assert "[Researcher] done" in merged
        assert "[Analyzer] done"   in merged
