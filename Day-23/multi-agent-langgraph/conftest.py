"""
conftest.py
Shared pytest fixtures used across all test files.

pytest automatically loads this file — no imports needed in test files.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path so tests can import modules
sys.path.insert(0, os.path.dirname(__file__))


# ── Auto-mock OpenAI client ───────────────────────────────────────────────────
# Prevents OpenAI() constructor from failing when OPENAI_API_KEY is not set.
# Applied to every test automatically — no real API calls are ever made.

@pytest.fixture(autouse=True)
def mock_openai_client():
    with patch("agents.base_agent.OpenAI") as mock_cls:
        mock_cls.return_value = MagicMock()
        yield mock_cls


# ── State fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def empty_state():
    """A fresh ResearchState with only the topic set."""
    return {
        "topic":            "artificial intelligence in healthcare",
        "search_results":   [],
        "analysis":         "",
        "critique":         "",
        "routing_decision": "",
        "final_report":     "",
        "iteration":        0,
        "status":           "pending",
        "log":              [],
    }


@pytest.fixture
def state_after_research(empty_state, sample_search_results):
    """State as it looks after the Researcher has run."""
    return {
        **empty_state,
        "search_results": sample_search_results,
        "iteration":      1,
        "status":         "researching",
    }


@pytest.fixture
def state_after_analysis(state_after_research):
    """State as it looks after the Analyzer has run."""
    return {
        **state_after_research,
        "analysis": "AI is transforming healthcare across diagnostics, drug discovery, and patient management.",
        "status":   "analyzing",
    }


# ── Data fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def sample_search_results():
    """Realistic search result dicts."""
    return [
        {
            "title":   "AI in Healthcare: Key Applications",
            "url":     "https://example.com/ai-healthcare",
            "snippet": "AI is transforming healthcare through improved diagnostics and drug discovery.",
        },
        {
            "title":   "Machine Learning in Medical Imaging",
            "url":     "https://example.com/ml-imaging",
            "snippet": "ML models match radiologist accuracy in detecting tumors from scans.",
        },
        {
            "title":   "Challenges of AI Adoption in Hospitals",
            "url":     "https://example.com/ai-challenges",
            "snippet": "Data privacy and legacy systems remain barriers to AI adoption.",
        },
    ]


@pytest.fixture
def sample_analysis():
    return (
        "AI is fundamentally reshaping healthcare across three key areas: "
        "diagnostics, drug discovery, and patient management. "
        "ML models have shown radiologist-level accuracy in medical imaging. "
        "However, data privacy regulations and legacy systems remain challenges."
    )


@pytest.fixture
def sample_critique():
    return (
        "The analysis covers the main themes but lacks specific statistics. "
        "Regulatory context (FDA approval process) is missing. "
        "Overall quality: adequate.\nROUTING: approved"
    )


# ── Mock OpenAI response ──────────────────────────────────────────────────────

@pytest.fixture
def mock_openai_response():
    """A realistic mock of openai.ChatCompletion response."""
    mock = MagicMock()
    mock.choices[0].message.content     = "This is a mocked LLM response."
    mock.choices[0].message.tool_calls  = None
    mock.choices[0].finish_reason       = "stop"
    mock.usage.prompt_tokens            = 100
    mock.usage.completion_tokens        = 50
    mock.usage.total_tokens             = 150
    mock.model                          = "gpt-4o-mini"
    return mock


# ── Mock agent state (attribute-access compatible) ────────────────────────────

class MockState:
    """
    Mimics the Day-22 dataclass interface so agent run() methods
    can be tested without importing ResearchState.
    """
    def __init__(self, **kwargs):
        self.topic            = kwargs.get("topic",            "test topic")
        self.search_results   = kwargs.get("search_results",   [])
        self.analysis         = kwargs.get("analysis",         "")
        self.critique         = kwargs.get("critique",         "")
        self.routing_decision = kwargs.get("routing_decision", "")
        self.final_report     = kwargs.get("final_report",     "")
        self.status           = kwargs.get("status",           "pending")
        self.iteration        = kwargs.get("iteration",        0)
        self._log             = []

    def add_log(self, agent_name: str, message: str):
        self._log.append(f"[{agent_name}] {message}")


@pytest.fixture
def mock_state():
    return MockState


@pytest.fixture
def mock_state_with_analysis(sample_analysis):
    return MockState(
        topic    = "AI in healthcare",
        analysis = sample_analysis,
    )


@pytest.fixture
def mock_state_with_results(sample_search_results):
    return MockState(
        topic          = "AI in healthcare",
        search_results = sample_search_results,
        iteration      = 1,
    )
