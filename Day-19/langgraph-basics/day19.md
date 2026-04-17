# Day 19 – LangGraph Basics

## Setup
```bash
pip install langgraph langchain-openai python-dotenv
```

## Deliverables

| File | Pattern |
|---|---|
| `examples/01_linear.py` | Linear graph: A → B → END |
| `examples/02_conditional.py` | Conditional routing based on LLM output |
| `examples/03_loop.py` | Retry loop with max attempts guard |
| `examples/04_multipath.py` | Three branches converging at one node |
| `examples/05_human_in_loop.py` | Pause/resume with MemorySaver + interrupt_before |
| `README.md` | Concept reference + API cheatsheet |

## Concepts Covered

### Building blocks
- **State** — `TypedDict` holding all data that flows through the graph
- **Node** — Python function: `(state) → dict of updates`
- **Edge** — fixed connection: `add_edge("a", "b")`
- **Conditional edge** — branching: router function returns next node name
- **END** — terminal constant that stops the graph

### Patterns
| Pattern | How |
|---|---|
| Linear | `add_edge` only |
| Conditional | `add_conditional_edges` with router function |
| Loop | Conditional edge pointing back to an earlier node |
| Multi-path | Multiple branches all connecting to one shared node |
| Human-in-the-loop | `MemorySaver` + `interrupt_before` + `update_state` + resume with `invoke(None)` |

### Visualisation
Stored at /graphs

### Human-in-the-loop flow
```
app.invoke(state, config)           # runs until interrupt
app.update_state(config, updates)   # human injects decision into state
app.invoke(None, config)            # resumes from checkpoint
```
