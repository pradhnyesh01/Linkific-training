# Day 18 – Agentic AI

No code today — research, design, and planning.

## Deliverables

| File | Description |
|---|---|
| `research-notes.md` | Agentic AI concepts: autonomy, ReAct, tools, memory, AutoGPT, BabyAGI |
| `architecture-diagram.md` | ASCII architecture + ReAct loop diagram (redraw in Excalidraw) |
| `project-proposal.md` | Full proposal for Research Assistant Agent |

## Key Concepts Learned

### What makes AI "agentic"
Autonomy + Tool use + Planning. An agent loops: Thought → Action → Observation until it reaches a goal.

### Agent types
- **Reactive**: input → output, no memory (basic chatbot)
- **Deliberative**: plans ahead with internal world model (chess AI)
- **Hybrid**: reactive tool calls + deliberative planning (ReAct agents)

### ReAct Pattern
```
Thought → Action (tool call) → Observation → Thought → ... → Final Answer
```
Most reliable pattern for LLM agents. The "Thought" step reduces hallucinations.

### Tools
Functions the LLM can call. Defined as JSON schemas. LLM decides when and how to call them.

### Memory types
| Type | Storage |
|---|---|
| In-context | Current prompt (lost on restart) |
| External | Database / vector DB (persistent) |

## Project Chosen
**Research Assistant Agent** — takes a research question, searches the web, reads results, returns a cited summary. Builds on Days 14–17 (LLMs + LangChain + RAG + FastAPI).
