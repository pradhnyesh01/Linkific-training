# Project Proposal – Research Assistant Agent

**Author:** Pradhnyesh Khorgade
**Internship:** Linkific AIML Internship
**Date:** April 2026

---

## 1. Problem Statement

When researching a topic, a person typically needs to:
- Search for information across multiple sources
- Read and filter relevant content
- Synthesise findings into a coherent summary
- Keep track of sources for credibility

This process is repetitive, time-consuming, and requires switching between multiple tools. An AI agent can automate the entire workflow — from searching to delivering a structured, cited summary — with a single natural language question.

---

## 2. Agent Capabilities

| Capability | Description |
|---|---|
| **Web search** | Find recent and relevant information on any topic |
| **Content reading** | Extract key information from web pages or uploaded documents |
| **Summarisation** | Condense long content into bullet points |
| **Calculation** | Handle any numerical analysis in the research |
| **Memory** | Remember the current research session and refer back to earlier findings |
| **Citation tracking** | Always record which source each fact came from |
| **Follow-up questions** | Handle clarifications without restarting the research |

---

## 3. Tools Needed

| Tool | Purpose | Implementation |
|---|---|---|
| `web_search(query)` | Search the internet for information | DuckDuckGo API or SerpAPI |
| `read_url(url)` | Fetch and extract text from a URL | BeautifulSoup + requests |
| `calculator(expression)` | Evaluate mathematical expressions safely | Python `eval` with sandbox |
| `document_reader(file)` | Extract text from uploaded PDFs/DOCX | PyPDF2, python-docx |
| `save_note(content)` | Save an intermediate finding to memory | In-memory dict or ChromaDB |
| `get_notes()` | Retrieve saved notes from this session | Returns saved dict |
| `final_answer(text)` | Signal that research is complete | Terminates the ReAct loop |

---

## 4. Expected Workflow

```
Step 1: User asks a research question
        e.g. "What is the current state of fusion energy research?"

Step 2: Agent plans sub-questions
        - What organisations are working on fusion?
        - What breakthroughs happened recently?
        - What are the remaining challenges?

Step 3: Agent searches for each sub-question
        - web_search("fusion energy 2026 breakthroughs")
        - web_search("ITER fusion reactor status 2026")

Step 4: Agent reads top results
        - read_url("https://...")
        - save_note("ITER achieved Q=1 milestone in early 2026")

Step 5: Agent checks if it has enough information
        - If yes → proceed to Step 6
        - If no  → search again with refined query

Step 6: Agent produces final answer
        - Structured summary with sections
        - Key facts as bullet points
        - All sources cited with URLs

Step 7: User can ask follow-up questions
        - Agent uses saved notes + history, no re-searching needed
```

---

## 5. Technical Architecture

```
User Input
    │
    ▼
FastAPI endpoint (POST /research)
    │
    ▼
RAGent (ReAct loop, GPT-4o)
    ├── web_search tool
    ├── read_url tool
    ├── calculator tool
    ├── document_reader tool
    └── memory (in-context + ChromaDB for long-term)
    │
    ▼
Structured Response
    {
      "summary": "...",
      "key_findings": [...],
      "sources": [...],
      "follow_up_suggestions": [...]
    }
```

---

## 6. Success Criteria

| Criterion | How to measure |
|---|---|
| **Accuracy** | Answer matches verified facts (manual spot-check on 10 questions) |
| **Source quality** | Every fact in the answer has a source URL |
| **Completeness** | Answer addresses all aspects of the question (manual review) |
| **Efficiency** | Completes research in ≤ 5 tool calls for a standard question |
| **Hallucination rate** | Agent says "I couldn't find information on that" rather than inventing facts |
| **Follow-up handling** | Can answer 3 follow-up questions without re-searching from scratch |

---

## 7. Scope and Limitations

**In scope:**
- Text-based research questions
- English language sources
- Questions answerable from publicly available web content

**Out of scope (for this version):**
- Real-time data (stock prices, live sports scores)
- Video or audio content processing
- Multi-user sessions (single user at a time)
- Paywalled content

---

## 8. Technologies

| Component | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini (function calling) |
| Agent framework | LangChain `AgentExecutor` or custom ReAct loop |
| Web search | DuckDuckGo Search API (free) |
| Memory | In-context (short-term) + ChromaDB (long-term) |
| API layer | FastAPI |
| Document processing | PyPDF2, python-docx |

---

## 9. Why This Use Case?

A research assistant agent is ideal for learning because:
1. It uses all core agent concepts (tools, ReAct, memory, planning)
2. Tools are simple to implement (search, read, save)
3. Results are easy to evaluate (is the answer accurate? are sources cited?)
4. It builds directly on Day-14 (LLMs), Day-15 (LangChain), Day-16/17 (RAG)
5. It has clear, real-world value
