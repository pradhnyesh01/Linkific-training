# Day-24: Testing, Logging, Cost Tracking & Docker

## Overview

Day-24 takes the multi-agent LangGraph system from Day-23 and makes it **production-ready**.
No new agents or features were added — the focus was entirely on code quality,
observability, and deployment.

---

## What Was Added

| Deliverable | Files | Status |
|-------------|-------|--------|
| Unit tests | `tests/test_state.py`, `tests/test_graph.py`, `tests/test_agents.py` | ✅ 45 tests, all passing |
| Integration tests | `tests/test_integration.py` | ✅ Full pipeline + loop tests |
| Test configuration | `conftest.py`, `pytest.ini` | ✅ |
| Logging | `logger.py` | ✅ File + console logging |
| Cost tracking | `cost_tracker.py` | ✅ Per-agent token + USD tracking |
| Log analysis | `log_analysis.py` | ✅ Parses and summarises log files |
| Environment config | `.env.example` | ✅ |
| Docker | `Dockerfile`, `docker-compose.yml` | ✅ |

---

## Project Structure

```
Day-23/multi-agent-langgraph/
│
├── agents/
│   ├── base_agent.py        ← logging + cost tracking integrated here
│   ├── researcher.py
│   ├── analyzer.py
│   ├── critic.py            ← outputs routing_decision
│   └── writer.py
│
├── tools/
│   └── web_search.py
│
├── tests/
│   ├── test_state.py        ← TypedDict structure + operator.add behaviour
│   ├── test_graph.py        ← StateAdapter + route_after_critic logic
│   ├── test_agents.py       ← per-agent logic (critic parsing, deduplication)
│   └── test_integration.py  ← full pipeline + re-research loop
│
├── logs/                    ← created at runtime (gitignored except .gitkeep)
│   └── agent_YYYYMMDD.log
│
├── state.py                 ← TypedDict ResearchState
├── graph.py                 ← LangGraph StateGraph
├── main.py                  ← entry point (with cost summary)
├── logger.py                ← centralised logging setup
├── cost_tracker.py          ← token usage + USD cost tracking
├── log_analysis.py          ← log file analysis script
├── conftest.py              ← shared pytest fixtures
├── pytest.ini               ← pytest configuration
├── .env.example             ← environment variable template
├── Dockerfile               ← container build instructions
├── docker-compose.yml       ← multi-service orchestration
└── requirements.txt
```

---

## Architecture

```
START ──► Researcher ──► Analyzer ──► Critic ──► Writer ──► END
               ▲                        │
               │   needs_more_research  │ approved
               └────────────────────────┘
                   (max 2 iterations)
```

### Agent Responsibilities

| Agent | Input | Output | Tools |
|-------|-------|--------|-------|
| Researcher | `topic` | `search_results` | `web_search` (DuckDuckGo) |
| Analyzer | `search_results` | `analysis` | None — LLM prompt |
| Critic | `analysis` | `critique` + `routing_decision` | None — LLM prompt |
| Writer | `analysis` + `critique` | `final_report` | None — LLM prompt |

---

## Setup

**1. Clone and navigate**
```bash
cd Day-23/multi-agent-langgraph
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

---

## Running

### Run the pipeline
```bash
python main.py

# Custom topic
python main.py "impact of quantum computing on cybersecurity"
```

### Run examples
```bash
python examples/01_simple_query.py    # simple topic — 1 research pass
python examples/02_complex_query.py   # broad topic — may trigger re-research
python examples/03_edge_cases.py      # vague topic, niche topic, iteration guard
```

### Analyse logs
```bash
python log_analysis.py

# Filter by specific date
python log_analysis.py --date 20240422
```

---

## Testing

### Run all tests
```bash
python -m pytest
```

### Run specific test file
```bash
python -m pytest tests/test_state.py
python -m pytest tests/test_graph.py
python -m pytest tests/test_agents.py
python -m pytest tests/test_integration.py
```

### Run with coverage report
```bash
pip install pytest-cov
python -m pytest --cov=. --cov-report=term-missing
```

### Test results
```
45 tests collected
45 passed in 0.30s
```

**No API calls are made during tests** — the OpenAI client is mocked in `conftest.py`
via `autouse=True`. Tests run in under 1 second and cost nothing.

### What is tested

| Test file | What it covers |
|-----------|---------------|
| `test_state.py` | TypedDict keys, types, defaults, `operator.add` accumulation |
| `test_graph.py` | `StateAdapter` reads/writes, `route_after_critic` all 9 edge cases |
| `test_agents.py` | Critic routing parsing, empty input handling, result deduplication |
| `test_integration.py` | Full pipeline happy path, re-research loop, max iteration guard |

---

## Logging

Every pipeline run writes to `logs/agent_YYYYMMDD.log`.

### Log levels
| Level | Where | What |
|-------|-------|------|
| DEBUG | File only | LLM call details, token counts, tool arguments |
| INFO | File + console | Agent decisions, routing, pipeline steps |
| WARNING | File + console | Retries, fallbacks, missing data |
| ERROR | File + console | Exceptions, failures |

### Sample log output
```
2024-04-22 14:30:01 | INFO     | main                 | Pipeline started — topic: AI in healthcare
2024-04-22 14:30:02 | DEBUG    | agent.researcher     | LLM call — 2 messages
2024-04-22 14:30:03 | INFO     | agent.researcher     | Tool call → web_search({'query': 'AI healthcare 2024'})
2024-04-22 14:30:05 | DEBUG    | agent.researcher     | LLM response — 312 tokens (in=280, out=32)
2024-04-22 14:30:14 | INFO     | cost_tracker         | Run complete — 4 calls, 2,847 tokens, $0.0021
2024-04-22 14:30:14 | INFO     | main                 | Pipeline complete
```

---

## Cost Tracking

Token usage and estimated cost are printed at the end of every run:

```
====================================================
  Cost Tracking Summary
====================================================
  Total API calls  : 5
  Input tokens     : 2,412
  Output tokens    :   435
  Total tokens     : 2,847
  Estimated cost   : $0.0021 USD

  Per-agent breakdown:
    Researcher       2 call(s)    980 tokens  $0.0006
    Analyzer         1 call(s)    720 tokens  $0.0005
    Critic           1 call(s)    650 tokens  $0.0005
    Writer           1 call(s)    497 tokens  $0.0005
====================================================
```

Pricing used (gpt-4o-mini):
- Input tokens: $0.150 per 1M tokens
- Output tokens: $0.600 per 1M tokens

---

## Docker

### Build and run
```bash
# Build image
docker build -t research-agent .

# Run with environment variables
docker run --env-file .env research-agent

# Run with custom topic
docker run --env-file .env research-agent python main.py "renewable energy trends"

# Run with docker compose (logs persist to ./logs/)
docker compose up
```

### Why Docker
Without Docker, running this project on another machine requires installing Python,
all packages, and configuring the environment manually.
With Docker, the entire environment is packaged — one command runs everything.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | LLM model to use |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

Copy `.env.example` to `.env` and fill in your values. Never commit `.env` to git.

---

## Key Concepts Learned

### Testing
- **pytest fixtures** — reusable setup code shared across test files via `conftest.py`
- **`autouse=True`** — automatically applied to every test without explicit request
- **Mocking** — `unittest.mock.patch` replaces real dependencies (OpenAI, web search) with fakes
- **Unit vs integration tests** — unit tests verify individual functions; integration tests verify the full workflow

### Logging
- **Log levels** — DEBUG for developer details, INFO for business events, WARNING/ERROR for problems
- **File + console handlers** — different detail levels for different audiences
- **Daily log rotation** — one file per day keeps logs manageable

### Cost Tracking
- **Token usage** from `response.usage` (prompt_tokens + completion_tokens)
- **Global singleton** — one `tracker` instance imported across all agents
- **Per-agent breakdown** — identifies which agent consumes the most tokens

### Docker
- **Dockerfile** — defines the environment (Python version, packages, code)
- **docker-compose.yml** — orchestrates services and volume mounts
- **`--env-file`** — passes secrets without baking them into the image
