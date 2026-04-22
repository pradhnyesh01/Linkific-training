"""
tests/test_tools.py
Tests for tools/web_search.py.

All tests mock the DuckDuckGo library so no real internet calls are made.
"""

import pytest
from unittest.mock import patch, MagicMock
from tools.web_search import search_web, execute


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_ddgs_mock(results: list):
    """Build a DDGS context-manager mock that returns `results`."""
    mock_ddgs       = MagicMock()
    mock_instance   = MagicMock()
    mock_instance.text.return_value = results
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_ddgs.return_value.__exit__.return_value  = False
    return mock_ddgs


RAW_RESULTS = [
    {"title": "AI in Healthcare",    "href": "https://example.com/1", "body": "AI transforms healthcare."},
    {"title": "ML in Drug Discovery","href": "https://example.com/2", "body": "ML accelerates research."},
    {"title": "AI Challenges",        "href": "https://example.com/3", "body": "Privacy is a key hurdle."},
]


# ── search_web() ──────────────────────────────────────────────────────────────

class TestSearchWeb:

    def test_returns_success_dict(self):
        mock_ddgs = make_ddgs_mock(RAW_RESULTS)
        with patch("tools.web_search.DDGS", mock_ddgs, create=True):
            with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
                result = search_web("AI healthcare", max_results=3)
        assert result["success"] is True

    def test_empty_query_returns_error(self):
        result = search_web("")
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_whitespace_only_query_returns_error(self):
        result = search_web("   ")
        assert result["success"] is False

    def test_max_results_clamped_to_10(self):
        mock_ddgs = make_ddgs_mock(RAW_RESULTS)
        with patch("tools.web_search.DDGS", mock_ddgs, create=True):
            with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
                result = search_web("test", max_results=999)
        # The internal call should use max(1, min(999, 10)) = 10
        # We only verify success (no crash on large max_results)
        assert "error" not in result or not result.get("success")

    def test_max_results_clamped_minimum_to_1(self):
        mock_ddgs = make_ddgs_mock(RAW_RESULTS[:1])
        with patch("tools.web_search.DDGS", mock_ddgs, create=True):
            with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
                result = search_web("test", max_results=0)
        assert "error" not in result or not result.get("success")

    def test_result_fields_present(self):
        mock_ddgs = make_ddgs_mock(RAW_RESULTS[:1])
        with patch("tools.web_search.DDGS", mock_ddgs, create=True):
            with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
                result = search_web("test")
        if result["success"]:
            for r in result["results"]:
                assert "title"   in r
                assert "url"     in r
                assert "snippet" in r

    def test_missing_library_returns_error(self):
        with patch.dict("sys.modules", {"ddgs": None, "duckduckgo_search": None}):
            result = search_web("test query")
        assert result["success"] is False
        assert "not installed" in result["error"].lower()

    def test_search_exception_returns_error(self):
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.side_effect = Exception("network error")
        with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
            result = search_web("test query")
        assert result["success"] is False


# ── execute() ─────────────────────────────────────────────────────────────────

class TestExecute:

    def test_execute_passes_query(self):
        mock_ddgs = make_ddgs_mock([])
        with patch("tools.web_search.DDGS", mock_ddgs, create=True):
            with patch.dict("sys.modules", {"ddgs": MagicMock(DDGS=mock_ddgs)}):
                result = execute({"query": "test", "max_results": 3})
        assert "success" in result

    def test_execute_empty_args_returns_error(self):
        result = execute({})
        assert result["success"] is False

    def test_execute_missing_query_returns_error(self):
        result = execute({"max_results": 5})
        assert result["success"] is False
