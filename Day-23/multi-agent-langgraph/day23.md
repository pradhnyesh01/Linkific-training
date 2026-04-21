# Day-23: Multi-Agent Research System with LangGraph

Extends Day-22's linear pipeline into a **conditional graph** using LangGraph.
The key addition: the Critic can send the pipeline back to the Researcher
for a second round of web searches if the analysis is inadequate.

---

## Architecture

```
                        ┌─────────────────────────────┐
                        │                             │
START ──► Researcher ──► Analyzer ──► Critic ──► Writer ──► END
               ▲                        │
               │   needs_more_research  │
               └────────────────────────┘
                   (max 2 iterations)
```

### Agents

| Agent | Role | Tools | Reads | Writes |
|-------|------|-------|-------|--------|
| **Researcher** | Searches the web | `web_search` (DuckDuckGo) | `topic` | `search_results` |
| **Analyzer** | Summarizes findings | LLM prompt | `search_results` | `analysis` |
| **Critic** | Reviews quality + decides routing | LLM prompt | `analysis` | `critique`, `routing_decision` |
| **Writer** | Produces final report | LLM prompt | `analysis`, `critique` | `final_report` |

### Routing Logic (Critic → next node)

```
routing_decision == "needs_more_research" AND iteration < 2  →  Researcher (loop)
routing_decision == "approved"  OR  iteration >= 2            →  Writer
```

The `iteration` cap ensures the pipeline always terminates — even if the Critic
keeps requesting more research, it stops after 2 research rounds.

---

## Shared State

```python
class ResearchState(TypedDict):
    topic:            str
    search_results:   Annotated[list[dict], operator.add]  # accumulates across loops
    analysis:         str
    critique:         str
    routing_decision: str    # "approved" | "needs_more_research"
    final_report:     str
    iteration:        int    # incremented each time Researcher runs
    log:              Annotated[list[str], operator.add]   # accumulates across all nodes
```

`Annotated[list, operator.add]` means LangGraph **appends** new items to the list
instead of replacing it. So on a second research pass, new search results are added
to the existing ones, giving the Analyzer more data.

---

## Day-22 vs Day-23

| Feature | Day-22 | Day-23 |
|---------|--------|--------|
| Orchestration | Plain Python (`coordinator.py`) | LangGraph `StateGraph` |
| State type | `@dataclass` | `TypedDict` |
| Pipeline | Fixed linear sequence | Conditional graph with loops |
| Critic output | Critique text only | Critique + routing decision |
| Re-research | Not possible | Up to 2 iterations |
| Infinite loop protection | N/A | `iteration >= 2` guard |

**Reused from Day-22 (unchanged):**
`base_agent.py`, `researcher.py`, `analyzer.py`, `writer.py`, `tools/web_search.py`

**Adapted for Day-23:**
`critic.py` — now outputs `routing_decision` field

**New in Day-23:**
`state.py` (TypedDict), `graph.py` (LangGraph graph + StateAdapter)

---

## Setup

```bash
cd Day-23/multi-agent-langgraph
pip install -r requirements.txt
```

Requires `OPENAI_API_KEY` in the root `.env` file.

---

## Run

```bash
# Default topic
python main.py

# Custom topic
python main.py "renewable energy storage technology"
```

### Examples

```bash
# Simple factual query — expect 1 research pass
python examples/01_simple_query.py

# Complex broad topic — may trigger re-research loop
python examples/02_complex_query.py

# Edge cases: vague topic, niche topic, max-iteration guard
python examples/03_edge_cases.py
```

---

## Project Structure

```
Day-23/multi-agent-langgraph/
├── state.py                   ← TypedDict ResearchState (LangGraph-compatible)
├── graph.py                   ← LangGraph StateGraph + node functions + routing
├── main.py                    ← entry point
├── agents/
│   ├── base_agent.py          ← BaseAgent with _chat() and _chat_with_tools()
│   ├── researcher.py          ← web search via function calling  [Day-22]
│   ├── analyzer.py            ← summarizes findings              [Day-22]
│   ├── critic.py              ← reviews + sets routing_decision  [adapted]
│   └── writer.py              ← produces final markdown report   [Day-22]
├── tools/
│   └── web_search.py          ← DuckDuckGo search                [Day-22]
├── examples/
│   ├── 01_simple_query.py     ← happy path test
│   ├── 02_complex_query.py    ← triggers potential re-research loop
│   └── 03_edge_cases.py       ← vague topic, niche topic, iteration guard
└── requirements.txt
```
