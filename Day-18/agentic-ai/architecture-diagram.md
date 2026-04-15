# Agent Architecture Diagram

Use this as a reference to draw in Excalidraw (excalidraw.com) or draw.io (app.diagrams.net).

---

## Chosen Use Case: Research Assistant Agent

The agent takes a research question, searches the web, reads relevant content,
and produces a structured summary with citations.

---

## Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              (CLI / Web UI / API endpoint)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │  research question
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATOR                              │
│                    (GPT-4o with ReAct)                         │
│                                                                 │
│   1. Receive question                                           │
│   2. Think: what do I need to find out?                        │
│   3. Choose a tool                                              │
│   4. Observe result                                             │
│   5. Repeat steps 2-4 until ready                              │
│   6. Generate final answer                                      │
└──────┬───────────┬───────────┬──────────────┬───────────────────┘
       │           │           │              │
       ▼           ▼           ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  WEB     │ │DOCUMENT  │ │CALCULATOR│ │   MEMORY     │
│  SEARCH  │ │ READER   │ │          │ │              │
│          │ │          │ │ Precise  │ │ Short-term:  │
│ Returns: │ │ Returns: │ │  math,   │ │ conversation │
│ snippets │ │ text     │ │  stats   │ │ history      │
│ + URLs   │ │ chunks   │ │          │ │              │
└──────────┘ └──────────┘ └──────────┘ │ Long-term:   │
                                        │ past research│
                                        │ (vector DB)  │
                                        └──────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                             │
│   - Answer to the question                                      │
│   - Key findings (bullet points)                                │
│   - Sources cited                                               │
│   - Confidence level                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## ReAct Loop Detail

```
┌──────────────────────────────────────────────────┐
│                  ReAct Loop                      │
│                                                  │
│   ┌─────────┐                                    │
│   │  START  │                                    │
│   └────┬────┘                                    │
│        │                                         │
│        ▼                                         │
│   ┌─────────┐     ┌──────────────────────────┐  │
│   │ THOUGHT │────▶│  "What do I need next?"  │  │
│   └────┬────┘     └──────────────────────────┘  │
│        │                                         │
│        ▼                                         │
│   ┌─────────┐     ┌──────────────────────────┐  │
│   │ ACTION  │────▶│  call_tool(name, args)   │  │
│   └────┬────┘     └──────────────────────────┘  │
│        │                                         │
│        ▼                                         │
│   ┌─────────────┐  ┌────────────────────────┐   │
│   │ OBSERVATION │─▶│  tool result returned  │   │
│   └──────┬──────┘  └────────────────────────┘   │
│          │                                       │
│          ▼                                       │
│   ┌─────────────────┐    ┌──────────────────┐   │
│   │  Have enough    │-No─▶  back to THOUGHT  │   │
│   │  information?   │    └──────────────────┘   │
│   └────────┬────────┘                           │
│            │ Yes                                 │
│            ▼                                     │
│   ┌──────────────┐                              │
│   │ FINAL ANSWER │                              │
│   └──────────────┘                              │
└──────────────────────────────────────────────────┘
```

---

## Data Flow for One Research Query

```
User: "What are the latest developments in quantum computing?"
  │
  ▼
Agent thinks: "I need recent news. I'll search the web first."
  │
  ├─▶ web_search("quantum computing developments 2026")
  │       └─▶ returns 5 snippets + URLs
  │
Agent thinks: "I have some info but need more depth on one result."
  │
  ├─▶ web_search("IBM quantum computing 2026 breakthrough")
  │       └─▶ returns more detailed content
  │
Agent thinks: "I have enough. I'll summarise with citations."
  │
  └─▶ final_answer(structured summary with bullet points + source URLs)
```

---

## Notes for Drawing in Excalidraw

When redrawing:
- Use **rounded rectangles** for components (Orchestrator, Tools, Memory)
- Use **diamond shapes** for decisions ("Have enough information?")
- Use **arrows with labels** to show data flow
- Group the tools in one swim lane, the ReAct loop in another
- Use colours: blue = LLM components, green = tools, orange = memory, grey = I/O
