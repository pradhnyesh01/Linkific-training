# Day 15 – LangChain Basics

## Setup

```bash
pip install langchain langchain-openai python-dotenv
```

Uses the same `.env` with `OPENAI_API_KEY` from Day-14.

---

## LangChain Concepts

### 1. Prompt Templates
Reusable prompts with named `{variable}` placeholders filled at runtime.

```python
template = PromptTemplate(
    input_variables=["topic", "audience"],
    template="Explain {topic} to a {audience} in 2 sentences."
)
```

- `PromptTemplate` — single string template
- `ChatPromptTemplate` — list of messages (system + human), supports roles

---

### 2. LLM Chain (LCEL pipe syntax)
Connect components with `|`. Output of each step feeds the next.

```
prompt | llm | output_parser
```

- `chain.invoke({...})` — run once
- `chain.batch([...])` — run on multiple inputs at once

---

### 3. Sequential Chain
Multiple LLM calls in sequence. Output of step N becomes input of step N+1.

```python
chain = step1 | (lambda x: {"key": x}) | step2
```

The `lambda` bridges the output name from step 1 to the variable name expected by step 2's prompt.

---

### 4. Conversation Memory
Stores chat history and injects it automatically into every prompt.

| Memory type | What it stores |
|---|---|
| `ConversationBufferMemory` | Full history (all turns) |
| `ConversationBufferWindowMemory(k=2)` | Only last `k` exchanges |

`ConversationChain` wraps the LLM + memory together. Use `.predict(input=...)` to chat.

---

### 5. Output Parsers

| Parser | Output type | Use when |
|---|---|---|
| `StrOutputParser` | `str` | Plain text response |
| `CommaSeparatedListOutputParser` | `list` | Need a Python list |
| `JsonOutputParser` | `dict` | Need structured data |

---

## Projects

| File | What it does |
|---|---|
| `projects/email_writer.py` | 2-step chain: draft → polish. Takes topic, tone, recipient. |
| `projects/text_summarizer.py` | Single chain with 4 selectable styles: bullet, tldr, executive, eli5 |
| `projects/chatbot.py` | Terminal chatbot with `ConversationBufferMemory`. Supports reset and history commands. |
| `projects/data_extractor.py` | Extracts structured JSON from invoice, resume, or news text |

Run any project:
```bash
cd Day-15/langchain-basics
python projects/email_writer.py
python projects/text_summarizer.py
python projects/data_extractor.py
python projects/chatbot.py        # interactive
```

---

## Chain Types Summary

```
Simple chain:     prompt → llm → parser
Sequential chain: prompt1 → llm → parser → lambda → prompt2 → llm → parser
Memory chain:     ConversationChain(llm, memory) — history auto-injected
```
