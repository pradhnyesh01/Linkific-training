# Day 18 – Agentic AI Research Notes

---

## 1. What Makes AI "Agentic"?

A regular LLM responds to one prompt and stops. An **agent** keeps going — it plans, acts, observes the result, and decides what to do next on its own.

Three properties make an AI system "agentic":

| Property | What it means | Example |
|---|---|---|
| **Autonomy** | Decides its own next steps without human input each time | Decides to search Google before answering |
| **Tool use** | Can call external functions, APIs, or services | Runs Python code, queries a database |
| **Planning** | Breaks a complex goal into sub-tasks and executes them in order | "To answer this, I need to: search → read → summarise → respond" |

---

## 2. Agent Types

### Reactive Agent
- Responds directly to current input, no memory of the past.
- Simple rule: `perception → action`
- Example: a chatbot that answers each message independently.
- **Weakness**: can't handle tasks that require remembering earlier context.

### Deliberative Agent
- Maintains an internal world model and plans ahead before acting.
- Slower but handles complex multi-step tasks.
- Example: a chess AI that thinks 10 moves ahead.
- **Weakness**: planning is expensive; can fail when the world model is wrong.

### Hybrid Agent (most modern AI agents)
- Combines reactive speed for simple sub-tasks with deliberative planning for the overall goal.
- Example: ReAct-pattern agents — fast tool calls, but a reasoning step decides which tool to call.

---

## 3. The ReAct Pattern (Reasoning + Acting)

ReAct is the most widely used pattern for LLM-based agents. Each step has three parts:

```
Thought:  "I need to find the current price of gold."
Action:   web_search("gold price today")
Observation: "Gold is trading at $2,340 per ounce as of April 2026."

Thought:  "I now have the price. I can answer the user."
Action:   final_answer("Gold is currently $2,340 per ounce.")
```

The agent loops: Thought → Action → Observation → Thought → ... until it has a final answer.

**Why it works:**
- Reasoning step makes the agent explain *why* it's calling a tool (reduces hallucination).
- Observation grounds the next reasoning step in real data.
- The loop can run as many times as needed.

---

## 4. Tool Usage and Function Calling

Tools are functions the agent can call. The LLM decides *when* and *with what arguments* to call them.

### How OpenAI Function Calling Works
1. You define tools as JSON schemas (name, description, parameters).
2. The LLM reads the tool descriptions and decides if/when to call one.
3. The LLM outputs a structured call: `{"name": "search", "arguments": {"query": "..."}}`
4. Your code executes the function and returns the result to the LLM.
5. The LLM uses the result to continue reasoning.

### Common Agent Tools
| Tool | What it does |
|---|---|
| Web search | Find current information from the internet |
| Code interpreter | Write and run Python code |
| Calculator | Do precise arithmetic |
| Database query | Read/write structured data |
| File reader | Extract text from uploaded documents |
| Email/calendar | Send messages, create events |
| HTTP request | Call any REST API |

---

## 5. Agent Memory and State

Without memory, an agent forgets everything between steps. There are four types:

| Type | What it stores | Lifespan |
|---|---|---|
| **In-context (short-term)** | The full conversation + tool outputs in the prompt | Current session only |
| **External (long-term)** | Summarised past sessions stored in a database | Persistent |
| **Episodic** | Specific past experiences ("last time I ran this query...") | Persistent |
| **Semantic** | Facts and knowledge (vector DB / RAG) | Persistent |

Most simple agents use only in-context memory. Production agents combine all four.

---

## 6. Research Examples

### AutoGPT
- One of the first open-source autonomous agents (2023).
- Given a high-level goal, it breaks it into tasks and executes them one by one using tools (web search, code, file I/O).
- **Problem**: tends to loop indefinitely on hard tasks; expensive API usage.
- **Lesson**: unbounded autonomy needs guard rails (max steps, human-in-the-loop checkpoints).

### BabyAGI
- Simpler than AutoGPT. Uses three agents: Task Creator, Task Prioritiser, Task Executor.
- Maintains a task list in a vector DB; completes tasks and adds new ones dynamically.
- **Lesson**: separating "what to do next" (planning) from "how to do it" (execution) is cleaner.

### GPT-4 with Function Calling
- Not a standalone agent framework — just the OpenAI API feature.
- The LLM itself decides when to call a function and with what arguments.
- Building block used inside AutoGPT, LangChain agents, LlamaIndex agents, etc.
- **Lesson**: function calling is the reliable, production-grade foundation for tool use.

---

## 7. Agent Patterns Summary

```
Simple Q&A:      User → LLM → Answer

ReAct Agent:     User → LLM → [Thought → Tool Call → Observation] × N → Answer

Multi-Agent:     User → Orchestrator Agent
                           ├── Research Agent (web search + summarise)
                           ├── Analyst Agent (data + calculations)
                           └── Writer Agent (format final output)
```

**When to use agents vs plain LLMs:**
- Use plain LLM: single-turn tasks, known inputs, no external data needed.
- Use agent: multi-step tasks, real-time data needed, decisions depend on intermediate results.
