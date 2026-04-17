"""
tools/database_query.py
Tool 3 – Database Query

Read-only SELECT queries against the Supabase PostgreSQL students table.
Uses the same DATABASE_URL already in the root .env (from Day-12).

Table schema:
  students (id INT, name TEXT, age INT, course TEXT, marks INT)

Safety rules:
  - Only SELECT is allowed (no INSERT / UPDATE / DELETE).
  - Column names are validated against a whitelist before use in SQL.
  - Values are passed via parameterized queries (%s), never interpolated.

Flow: execute(args) → query_students(...) → {"success": True/False, ...}

Dependency: pip install psycopg2-binary
"""

import os
from typing import Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
DATABASE_URL = os.getenv("DATABASE_URL")

# Whitelisted column names — only these are accepted in filter_by / order_by
_VALID_COLUMNS = {"id", "name", "age", "course", "marks"}

# Supported aggregate operations
_AGGREGATE_SQL = {
    "count":     "SELECT COUNT(*) FROM students",
    "avg_marks": "SELECT AVG(marks) FROM students",
    "max_marks": "SELECT MAX(marks) FROM students",
    "min_marks": "SELECT MIN(marks) FROM students",
}


# ── Core function ─────────────────────────────────────────────────────────────

def query_students(
    filter_by:   str = None,
    filter_value: str = None,
    order_by:    str = None,
    limit:       int = 10,
    aggregate:   str = None,
) -> dict[str, Any]:
    """
    Query the students table (read-only).

    Args:
        filter_by    : column to filter on (id/name/age/course/marks), optional
        filter_value : value to match (cast to appropriate type internally)
        order_by     : column to sort by, optionally with " DESC" suffix
        limit        : max rows to return (1–100), default 10
        aggregate    : one of count / avg_marks / max_marks / min_marks

    Returns:
        {"success": True, "query_type": "select", "row_count": int, "rows": [...]}
        {"success": True, "query_type": aggregate, "result": float | int}
        {"success": False, "error": str}
    """
    if not DATABASE_URL:
        return {"success": False, "error": "DATABASE_URL not found in environment."}

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        return {"success": False, "error": "psycopg2 not installed. Run: pip install psycopg2-binary"}

    conn = None
    cur  = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")

        # ── Aggregate query ───────────────────────────────────────────────────
        if aggregate:
            aggregate = aggregate.strip().lower()
            sql = _AGGREGATE_SQL.get(aggregate)
            if sql is None:
                return {
                    "success": False,
                    "error":   f"Unknown aggregate: '{aggregate}'. "
                               "Choose from: count, avg_marks, max_marks, min_marks.",
                }
            cur = conn.cursor()
            cur.execute(sql)
            value = cur.fetchone()[0]
            return {
                "success":    True,
                "query_type": aggregate,
                "result":     float(value) if value is not None else None,
            }

        # ── SELECT query ──────────────────────────────────────────────────────
        limit = max(1, min(int(limit), 100))
        params = []
        where_clause = ""

        if filter_by:
            col = filter_by.strip().lower()
            if col not in _VALID_COLUMNS:
                return {"success": False, "error": f"Invalid column: '{col}'. "
                        f"Valid columns: {sorted(_VALID_COLUMNS)}."}
            # Try numeric cast for numeric columns
            if col in ("id", "age", "marks"):
                try:
                    filter_value = int(filter_value)
                except (ValueError, TypeError):
                    return {"success": False, "error": f"Column '{col}' expects an integer value."}
            where_clause = f" WHERE {col} = %s"
            params.append(filter_value)

        order_clause = ""
        if order_by:
            order_str = order_by.strip()
            order_col = order_str.replace(" DESC", "").replace(" ASC", "").strip().lower()
            if order_col not in _VALID_COLUMNS:
                return {"success": False, "error": f"Invalid order_by column: '{order_col}'."}
            direction = "DESC" if "DESC" in order_str.upper() else "ASC"
            order_clause = f" ORDER BY {order_col} {direction}"

        sql = f"SELECT id, name, age, course, marks FROM students{where_clause}{order_clause} LIMIT %s"
        params.append(limit)

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

        return {
            "success":    True,
            "query_type": "select",
            "row_count":  len(rows),
            "rows":       rows,
        }

    except Exception as e:
        return {"success": False, "error": f"Database error: {e}"}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()



def execute(args: dict) -> dict:
    return query_students(
        filter_by    = args.get("filter_by"),
        filter_value = args.get("filter_value"),
        order_by     = args.get("order_by"),
        limit        = args.get("limit", 10),
        aggregate    = args.get("aggregate"),
    )



if __name__ == "__main__":
    import json

    tests = [
        {},                                                          # all students (limit 10)
        {"filter_by": "course", "filter_value": "Mathematics"},     # filter by course
        {"order_by": "marks DESC", "limit": 5},                     # top 5 by marks
        {"aggregate": "avg_marks"},                                  # average marks
        {"aggregate": "count"},                                      # total count
        {"filter_by": "hacker_col", "filter_value": "x"},           # error: bad column
    ]

    for t in tests:
        result = execute(t)
        if result["success"]:
            if result.get("query_type") == "select":
                print(f"Rows returned: {result['row_count']}")
                for r in result["rows"][:3]:
                    print(f"  {r}")
            else:
                print(f"{result['query_type']}: {result['result']}")
        else:
            print(f"Error: {result['error']}")
        print()
