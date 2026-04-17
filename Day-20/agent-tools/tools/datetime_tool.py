"""
tools/datetime_tool.py
Tool 7 – Date & Time

Provides date/time operations using only Python stdlib.
No external dependencies, no API keys required.

Operations:
  now           – current UTC datetime
  add_days      – add N days to a date
  subtract_days – subtract N days from a date
  day_of_week   – return weekday name for a date
  format_date   – apply a strftime format string to a date
  days_between  – count calendar days between two dates
  is_weekend    – check if a date falls on Saturday or Sunday

Flow: execute(args) → datetime_operation(...) → {"success": True/False, ...}
"""

from datetime import datetime, timedelta
from typing import Any
import calendar



_DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]

def _parse_date(date_str: str) -> datetime | None:
    """Try parsing date_str against known formats. Returns None on failure."""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def _weekday_name(dt: datetime) -> str:
    return calendar.day_name[dt.weekday()]


# ── Core function ─────────────────────────────────────────────────────────────

def datetime_operation(
    operation:  str,
    date_str:   str  = None,
    days:       int  = None,
    format_str: str  = None,
) -> dict[str, Any]:
    """
    Perform a date/time operation.

    Args:
        operation  : see module docstring for list
        date_str   : ISO date "YYYY-MM-DD" (or two dates "d1,d2" for days_between)
        days       : integer offset for add_days / subtract_days
        format_str : strftime format string for format_date (e.g. "%B %d, %Y")

    Returns:
        {"success": True, "operation": ..., ...result fields...}
        {"success": False, "error": str}
    """
    operation = operation.strip().lower()

    if operation == "now":
        now = datetime.utcnow()
        return {
            "success":     True,
            "operation":   "now",
            "datetime":    now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "date":        now.strftime("%Y-%m-%d"),
            "time":        now.strftime("%H:%M:%S"),
            "weekday":     _weekday_name(now),
            "weekday_num": now.weekday(),   # 0=Monday
            "timezone":    "UTC",
        }

    # ── add_days / subtract_days ──────────────────────────────────────────────
    if operation in ("add_days", "subtract_days"):
        if not date_str:
            return {"success": False, "error": f"'date_str' is required for {operation}."}
        if days is None:
            return {"success": False, "error": f"'days' is required for {operation}."}
        dt = _parse_date(date_str)
        if dt is None:
            return {"success": False, "error": f"Cannot parse date: '{date_str}'. Use YYYY-MM-DD."}
        delta = timedelta(days=int(days))
        result_dt = dt + delta if operation == "add_days" else dt - delta
        return {
            "success":       True,
            "operation":     operation,
            "original_date": dt.strftime("%Y-%m-%d"),
            "days":          int(days),
            "result_date":   result_dt.strftime("%Y-%m-%d"),
            "result_weekday": _weekday_name(result_dt),
        }

    # ── day_of_week ───────────────────────────────────────────────────────────
    if operation == "day_of_week":
        if not date_str:
            return {"success": False, "error": "'date_str' is required for day_of_week."}
        dt = _parse_date(date_str)
        if dt is None:
            return {"success": False, "error": f"Cannot parse date: '{date_str}'."}
        return {
            "success":     True,
            "operation":   "day_of_week",
            "date":        dt.strftime("%Y-%m-%d"),
            "weekday":     _weekday_name(dt),
            "weekday_num": dt.weekday(),
        }

    # ── format_date ───────────────────────────────────────────────────────────
    if operation == "format_date":
        if not date_str:
            return {"success": False, "error": "'date_str' is required for format_date."}
        if not format_str:
            return {"success": False, "error": "'format_str' is required for format_date."}
        dt = _parse_date(date_str)
        if dt is None:
            return {"success": False, "error": f"Cannot parse date: '{date_str}'."}
        try:
            formatted = dt.strftime(format_str)
        except Exception as e:
            return {"success": False, "error": f"Invalid format string: {e}"}
        return {
            "success":    True,
            "operation":  "format_date",
            "date":       dt.strftime("%Y-%m-%d"),
            "format_str": format_str,
            "result":     formatted,
        }

    # ── days_between ──────────────────────────────────────────────────────────
    if operation == "days_between":
        if not date_str or "," not in date_str:
            return {"success": False,
                    "error": "'date_str' must be two dates separated by comma: 'YYYY-MM-DD,YYYY-MM-DD'."}
        parts = date_str.split(",", 1)
        dt1 = _parse_date(parts[0])
        dt2 = _parse_date(parts[1])
        if dt1 is None or dt2 is None:
            return {"success": False, "error": f"Cannot parse one or both dates: '{date_str}'."}
        delta = abs((dt2 - dt1).days)
        return {
            "success":   True,
            "operation": "days_between",
            "date1":     dt1.strftime("%Y-%m-%d"),
            "date2":     dt2.strftime("%Y-%m-%d"),
            "days":      delta,
        }

    # ── is_weekend ────────────────────────────────────────────────────────────
    if operation == "is_weekend":
        if not date_str:
            return {"success": False, "error": "'date_str' is required for is_weekend."}
        dt = _parse_date(date_str)
        if dt is None:
            return {"success": False, "error": f"Cannot parse date: '{date_str}'."}
        is_wknd = dt.weekday() >= 5   # 5=Saturday, 6=Sunday
        return {
            "success":    True,
            "operation":  "is_weekend",
            "date":       dt.strftime("%Y-%m-%d"),
            "weekday":    _weekday_name(dt),
            "is_weekend": is_wknd,
        }

    return {
        "success": False,
        "error": f"Unknown operation: '{operation}'. Choose from: "
                 "now, add_days, subtract_days, day_of_week, format_date, days_between, is_weekend.",
    }



def execute(args: dict) -> dict:
    return datetime_operation(
        operation  = args.get("operation", ""),
        date_str   = args.get("date_str"),
        days       = args.get("days"),
        format_str = args.get("format_str"),
    )



if __name__ == "__main__":
    import json
    tests = [
        {"operation": "now"},
        {"operation": "add_days",      "date_str": "2026-04-17", "days": 30},
        {"operation": "subtract_days", "date_str": "2026-04-17", "days": 7},
        {"operation": "day_of_week",   "date_str": "2026-01-01"},
        {"operation": "format_date",   "date_str": "2026-04-17", "format_str": "%B %d, %Y"},
        {"operation": "days_between",  "date_str": "2026-01-01,2026-04-17"},
        {"operation": "is_weekend",    "date_str": "2026-04-19"},   # Sunday
        {"operation": "unknown"},
        {"operation": "add_days",      "date_str": "not-a-date",    "days": 5},
    ]
    for t in tests:
        result = execute(t)
        print(json.dumps(result, indent=2))
        print()
