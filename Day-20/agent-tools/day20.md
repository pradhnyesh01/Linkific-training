# Day 20 – Agent Tools & Function Calling

## Overview

```
User Question
    │
    ▼
OpenAI gpt-4o-mini  +  TOOLS_LIST (8 schemas)
    │
    ├─ tool_calls → Tool Executor → Result → back to OpenAI
    │
    └─ stop → Final Answer
```

The agent calls tools automatically based on the question. Each tool always returns `{"success": True/False, ...}` — errors are never raised as exceptions.

**No new API keys needed.** Uses `OPENAI_API_KEY` and `DATABASE_URL` from the root `.env`.

---

## Setup

```bash
cd Day-20/agent-tools
pip install openai python-dotenv psycopg2-binary duckduckgo-search pandas
```

---

## Tool Catalog

| # | Tool | File | Key Parameters | Returns |
|---|------|------|----------------|---------|
| 1 | **Calculator** | `tools/calculator.py` | `operation`, `a`, `b` | Numeric result |
| 2 | **Web Search** | `tools/web_search.py` | `query`, `max_results` | List of `{title, url, snippet}` |
| 3 | **Database Query** | `tools/database_query.py` | `filter_by`, `aggregate`, `limit` | Student rows or aggregate value |
| 4 | **File Reader** | `tools/file_reader.py` | `file_path`, `max_lines` | File content or structured summary |
| 5 | **Weather** | `tools/weather.py` | `city`, `units` | Temp, humidity, wind, condition |
| 6 | **Email Sender** | `tools/email_sender.py` | `to`, `subject`, `body` | Simulated send + message ID |
| 7 | **Datetime** | `tools/datetime_tool.py` | `operation`, `date_str`, `days` | Date/time result |
| 8 | **Data Analyzer** | `tools/data_analyzer.py` | `source`, `operation`, `column` | Stats, filter, groupby result |

---

## Quick Start

```python
from function_calling import run_agent

result = run_agent("What is 15% of 847?")
print(result["answer"])
# → 127.05
```

---

## How Function Calling Works

1. **Define schemas** — each tool has a JSON schema describing its name, description, and parameters
2. **Pass to OpenAI** — send `tools=TOOLS_LIST` in the chat completion request
3. **Check `finish_reason`** — if `"tool_calls"`, the model wants to invoke a tool
4. **Parse arguments** — `json.loads(tool_call.function.arguments)` (always a JSON string)
5. **Execute tool** — dispatch to `TOOL_EXECUTORS[fn_name](args)`
6. **Return result** — append `role:"tool"` message with `tool_call_id` + result
7. **Loop** — call OpenAI again until `finish_reason == "stop"`

---

## Direct Tool Usage (No LLM)

```python
from tools.calculator   import execute as calc
from tools.weather      import execute as weather
from tools.datetime_tool import execute as dt

calc({"operation": "sqrt", "a": 144})
# → {"success": True, "result": 12.0, ...}

weather({"city": "London", "units": "celsius"})
# → {"success": True, "temperature": 14.0, "condition": "Partly cloudy", ...}

dt({"operation": "add_days", "date_str": "2026-04-17", "days": 30})
# → {"success": True, "result_date": "2026-05-17", ...}
```

---

## Running Examples

```bash
cd Day-20/agent-tools

# Test all 8 tools directly (no LLM)
python examples/01_basic_calls.py

# Multi-tool agent chaining
python examples/02_tool_chaining.py

# Error handling tests
python examples/03_error_handling.py

# Interactive notebook
jupyter notebook testing_notebook.ipynb
```

---

## Architecture

```
agent-tools/
├── tools/              ← 8 tool files, each with execute(args) -> dict
├── tool_schemas.py     ← OpenAI JSON schemas for all 8 tools
├── function_calling.py ← Agent loop (run_agent)
├── examples/           ← 3 runnable examples
├── sample_data/        ← sample.txt, sample.csv, sample.json
└── logs/               ← email_log.txt (created at runtime)
```

---

## Error Handling Philosophy

- Every `execute()` function catches all exceptions internally
- Success: `{"success": True, ...result fields...}`
- Failure: `{"success": False, "error": "descriptive message"}`
- The agent loop also wraps tool calls in `try/except` as a final safety net
- The model sees errors in the tool result and explains them gracefully to the user

---

## Tool Operations Reference

| Tool | Operations / Values |
|------|---------------------|
| **Calculator** | `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt`, `percentage` |
| **Web Search** | `query` (string), `max_results` (1–10) |
| **Database** | `filter_by` (id/name/age/course/marks), `aggregate` (count/avg_marks/max_marks/min_marks) |
| **File Reader** | `.txt`, `.csv`, `.json` |
| **Weather** | `units`: `celsius` or `fahrenheit` |
| **Email** | `priority`: `low`, `normal`, `high` |
| **Datetime** | `now`, `add_days`, `subtract_days`, `day_of_week`, `format_date`, `days_between`, `is_weekend` |
| **Data Analyzer** | `describe`, `groupby`, `filter`, `correlation`, `value_counts`, `top_n` |

---

## Free APIs Used (No Key Needed)

| API | Used by | Notes |
|-----|---------|-------|
| Open-Meteo geocoding | `weather.py` | `geocoding-api.open-meteo.com` |
| Open-Meteo forecast | `weather.py` | `api.open-meteo.com` |
| DuckDuckGo search | `web_search.py` | via `duckduckgo-search` library |
