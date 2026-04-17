"""
tool_schemas.py
All 8 OpenAI function-calling schemas in one place.

Usage:
    from tool_schemas import TOOLS_LIST, TOOLS_BY_NAME
    response = client.chat.completions.create(model=..., messages=..., tools=TOOLS_LIST)

Each schema follows the OpenAI format:
    {"type": "function", "function": {"name": ..., "description": ..., "parameters": {...}}}
"""


# ── Tool 1: Calculator ────────────────────────────────────────────────────────

CALCULATOR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Perform arithmetic operations. Supported: add, subtract, multiply, divide, "
            "power (a^b), sqrt (square root of a), percentage (a% of b)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt", "percentage"],
                    "description": "The arithmetic operation to perform.",
                },
                "a": {
                    "type": "number",
                    "description": "First operand.",
                },
                "b": {
                    "type": "number",
                    "description": "Second operand. Not required for sqrt.",
                },
            },
            "required": ["operation", "a"],
        },
    },
}


# ── Tool 2: Web Search ────────────────────────────────────────────────────────

WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the internet using DuckDuckGo. Returns titles, URLs, and snippets "
            "for the top matching results. Use for current events, facts, or any information "
            "that may not be in the model's training data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (1–10). Default is 5.",
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
        },
    },
}


# ── Tool 3: Database Query ────────────────────────────────────────────────────

DATABASE_QUERY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "database_query",
        "description": (
            "Query the students database (PostgreSQL). The table has columns: "
            "id (int), name (text), age (int), course (text), marks (int). "
            "Supports filtering, sorting, and aggregation. Read-only."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filter_by": {
                    "type": "string",
                    "enum": ["id", "name", "age", "course", "marks"],
                    "description": "Column to filter on.",
                },
                "filter_value": {
                    "type": "string",
                    "description": "Value to match in filter_by column.",
                },
                "order_by": {
                    "type": "string",
                    "description": "Column to sort by (e.g. 'marks DESC', 'name ASC').",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return (1–100). Default 10.",
                    "minimum": 1,
                    "maximum": 100,
                },
                "aggregate": {
                    "type": "string",
                    "enum": ["count", "avg_marks", "max_marks", "min_marks"],
                    "description": "Run an aggregate query instead of returning rows.",
                },
            },
            "required": [],
        },
    },
}


# ── Tool 4: File Reader ───────────────────────────────────────────────────────

FILE_READER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_reader",
        "description": (
            "Read and return the contents of a file. "
            "Supports .txt (returns lines), .csv (returns rows as dicts), "
            "and .json (returns parsed object)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Max lines/rows to return (1–200). Default 50.",
                    "minimum": 1,
                    "maximum": 200,
                },
            },
            "required": ["file_path"],
        },
    },
}


# ── Tool 5: Weather ───────────────────────────────────────────────────────────

WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "weather",
        "description": (
            "Get the current weather conditions for any city in the world. "
            "Returns temperature, humidity, wind speed, and weather condition description. "
            "No API key required."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city (e.g. 'London', 'Mumbai', 'New York').",
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Default is celsius.",
                },
            },
            "required": ["city"],
        },
    },
}


# ── Tool 6: Email Sender ──────────────────────────────────────────────────────

EMAIL_SENDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "email_sender",
        "description": (
            "Simulate sending an email. No real email is sent — the action is logged "
            "to a local file and confirmed with a message ID. Useful for drafting and "
            "confirming email actions in workflows."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address.",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line.",
                },
                "body": {
                    "type": "string",
                    "description": "Email body text.",
                },
                "cc": {
                    "type": "string",
                    "description": "Optional CC email address.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "description": "Email priority. Default is normal.",
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
}


# ── Tool 7: Datetime Tool ─────────────────────────────────────────────────────

DATETIME_SCHEMA = {
    "type": "function",
    "function": {
        "name": "datetime_tool",
        "description": (
            "Perform date and time operations. "
            "Get the current UTC time, add or subtract days from a date, "
            "find the day of the week, format a date, count days between two dates, "
            "or check if a date is a weekend."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "now", "add_days", "subtract_days",
                        "day_of_week", "format_date", "days_between", "is_weekend",
                    ],
                    "description": "The date/time operation to perform.",
                },
                "date_str": {
                    "type": "string",
                    "description": (
                        "Date in YYYY-MM-DD format. For days_between, provide two dates "
                        "separated by a comma: 'YYYY-MM-DD,YYYY-MM-DD'."
                    ),
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to add or subtract.",
                },
                "format_str": {
                    "type": "string",
                    "description": "strftime format string for format_date (e.g. '%B %d, %Y').",
                },
            },
            "required": ["operation"],
        },
    },
}


# ── Tool 8: Data Analyzer ─────────────────────────────────────────────────────

DATA_ANALYZER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "data_analyzer",
        "description": (
            "Analyze CSV data using pandas. Load data from a file path or an inline CSV string. "
            "Supports: describe (stats), groupby, filter rows, correlation matrix, "
            "value counts, or returning top N rows."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "File path to a CSV file, or raw CSV text if source_type is 'inline'.",
                },
                "source_type": {
                    "type": "string",
                    "enum": ["file", "inline"],
                    "description": "Whether source is a file path or inline CSV string. Default: 'file'.",
                },
                "operation": {
                    "type": "string",
                    "enum": ["describe", "groupby", "filter", "correlation", "value_counts", "top_n"],
                    "description": "Analysis operation to run. Default: 'describe'.",
                },
                "column": {
                    "type": "string",
                    "description": "Column name required for value_counts.",
                },
                "group_by": {
                    "type": "string",
                    "description": "Column name to group by for groupby operation.",
                },
                "filter_column": {
                    "type": "string",
                    "description": "Column to filter on for filter operation.",
                },
                "filter_value": {
                    "type": "string",
                    "description": "Value to match in filter_column.",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of rows/results to return. Default 10.",
                },
            },
            "required": ["source"],
        },
    },
}


# ── Master list passed to OpenAI ──────────────────────────────────────────────

TOOLS_LIST = [
    CALCULATOR_SCHEMA,
    WEB_SEARCH_SCHEMA,
    DATABASE_QUERY_SCHEMA,
    FILE_READER_SCHEMA,
    WEATHER_SCHEMA,
    EMAIL_SENDER_SCHEMA,
    DATETIME_SCHEMA,
    DATA_ANALYZER_SCHEMA,
]

# ── Schema lookup by tool name ─────────────────────────────────────────────────

TOOLS_BY_NAME = {schema["function"]["name"]: schema for schema in TOOLS_LIST}


if __name__ == "__main__":
    print(f"Total tools registered: {len(TOOLS_LIST)}")
    for schema in TOOLS_LIST:
        fn    = schema["function"]
        props = fn["parameters"]["properties"]
        req   = fn["parameters"].get("required", [])
        print(f"  • {fn['name']:20s}  params={len(props)}  required={req}")
