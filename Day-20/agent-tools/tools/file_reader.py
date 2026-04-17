"""
tools/file_reader.py
Tool 4 – File Reader

Reads and returns content from .txt, .csv, and .json files.
Uses only Python stdlib — no external dependencies.

Flow: execute(args) → read_file(file_path, max_lines) → {"success": True/False, ...}
"""

import os
import csv
import json
from typing import Any


SUPPORTED_EXTENSIONS = {".txt", ".csv", ".json"}


# ── Core function ─────────────────────────────────────────────────────────────

def read_file(file_path: str, max_lines: int = 50) -> dict[str, Any]:
    """
    Read a file and return its content or a structured summary.

    Args:
        file_path : path to the file (absolute or relative)
        max_lines : maximum lines/rows to return for .txt and .csv (1–200)

    Returns:
        Varies by file type — see below.
        {"success": False, "error": str} on failure.
    """
    if not file_path or not file_path.strip():
        return {"success": False, "error": "file_path cannot be empty."}

    file_path = file_path.strip()
    max_lines = max(1, min(int(max_lines), 200))

    # ── Existence check ───────────────────────────────────────────────────────
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: '{file_path}'."}

    if not os.path.isfile(file_path):
        return {"success": False, "error": f"Not a file: '{file_path}'."}

    # ── Extension check ───────────────────────────────────────────────────────
    _, ext = os.path.splitext(file_path.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "success": False,
            "error":   f"Unsupported file type: '{ext}'. Supported: .txt, .csv, .json.",
        }

    # ── .txt ──────────────────────────────────────────────────────────────────
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
            total     = len(all_lines)
            shown     = min(total, max_lines)
            content   = [line.rstrip("\n") for line in all_lines[:shown]]
            return {
                "success":     True,
                "file_type":   "txt",
                "file_path":   file_path,
                "total_lines": total,
                "shown_lines": shown,
                "content":     content,
            }
        except Exception as e:
            return {"success": False, "error": f"Read error: {e}"}

    # ── .csv ──────────────────────────────────────────────────────────────────
    if ext == ".csv":
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace", newline="") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []
                all_rows = list(reader)
            total   = len(all_rows)
            shown   = min(total, max_lines)
            rows    = [dict(r) for r in all_rows[:shown]]
            return {
                "success":    True,
                "file_type":  "csv",
                "file_path":  file_path,
                "columns":    list(columns),
                "total_rows": total,
                "shown_rows": shown,
                "rows":       rows,
            }
        except Exception as e:
            return {"success": False, "error": f"CSV parse error: {e}"}

    # ── .json ─────────────────────────────────────────────────────────────────
    if ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data_type = "array" if isinstance(data, list) else "object"
            length    = len(data) if isinstance(data, (list, dict)) else None
            # Truncate long arrays
            content = data[:max_lines] if isinstance(data, list) and len(data) > max_lines else data
            return {
                "success":   True,
                "file_type": "json",
                "file_path": file_path,
                "data_type": data_type,
                "length":    length,
                "content":   content,
            }
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON parse error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Read error: {e}"}

    # Fallback (should not reach here)
    return {"success": False, "error": "Unexpected error reading file."}



def execute(args: dict) -> dict:
    return read_file(
        file_path = args.get("file_path", ""),
        max_lines = args.get("max_lines", 50),
    )



if __name__ == "__main__":
    import json as _json
    import os

    base = os.path.join(os.path.dirname(__file__), "..", "sample_data")

    tests = [
        {"file_path": os.path.join(base, "sample.txt"),  "max_lines": 5},
        {"file_path": os.path.join(base, "sample.csv"),  "max_lines": 3},
        {"file_path": os.path.join(base, "sample.json")},
        {"file_path": "/nonexistent/path/file.txt"},       # error: not found
        {"file_path": os.path.join(base, "sample.csv"),   "max_lines": 1},  # unsupported via .pdf test replaced
    ]

    for t in tests:
        result = execute(t)
        print(_json.dumps(result, indent=2))
        print()
