"""
tools/data_analyzer.py
Tool 8 – Data Analyzer

Loads CSV data (from file path or inline CSV string) and runs statistical
analysis using pandas.

Operations:
  describe      – descriptive statistics for all columns
  groupby       – group by a column and compute aggregates on numeric columns
  filter        – filter rows where filter_column == filter_value
  correlation   – correlation matrix for numeric columns
  value_counts  – frequency count for a categorical column
  top_n         – return the first N rows

Flow: execute(args) → analyze_data(...) → {"success": True/False, ...}

Dependency: pip install pandas
"""

import io
from typing import Any


# ── Core function ─────────────────────────────────────────────────────────────

def analyze_data(
    source:        str,
    source_type:   str  = "file",
    operation:     str  = "describe",
    column:        str  = None,
    group_by:      str  = None,
    filter_column: str  = None,
    filter_value:  str  = None,
    top_n:         int  = 10,
) -> dict[str, Any]:
    """
    Load CSV data and perform statistical analysis.

    Args:
        source        : file path (source_type="file") or raw CSV string (source_type="inline")
        source_type   : "file" or "inline"
        operation     : describe / groupby / filter / correlation / value_counts / top_n
        column        : column for value_counts / top_n
        group_by      : column for groupby
        filter_column : column to filter on
        filter_value  : value to match in filter_column
        top_n         : number of results for top_n (default 10)

    Returns:
        {"success": True, "operation": ..., "shape": [...], "columns": [...], "result": ...}
        {"success": False, "error": str}
    """
    try:
        import pandas as pd
    except ImportError:
        return {"success": False, "error": "pandas not installed. Run: pip install pandas"}

    if not source or not source.strip():
        return {"success": False, "error": "'source' cannot be empty."}

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        if source_type == "inline":
            df = pd.read_csv(io.StringIO(source.strip()))
        else:   # "file"
            import os
            if not os.path.exists(source):
                return {"success": False, "error": f"File not found: '{source}'."}
            df = pd.read_csv(source)
    except Exception as e:
        return {"success": False, "error": f"Parse error: {e}"}

    shape   = list(df.shape)
    columns = list(df.columns)

    dtypes = {col: str(df[col].dtype) for col in columns}

    operation = operation.strip().lower()

    # ── describe ──────────────────────────────────────────────────────────────
    if operation == "describe":
        try:
            stats = df.describe(include="all").fillna("").to_dict()
            # Convert numpy types to Python native for JSON serialization
            stats = _convert(stats)
            return {"success": True, "operation": "describe",
                    "shape": shape, "columns": columns, "dtypes": dtypes, "result": stats}
        except Exception as e:
            return {"success": False, "error": f"describe failed: {e}"}

    # ── groupby ───────────────────────────────────────────────────────────────
    if operation == "groupby":
        if not group_by:
            return {"success": False, "error": "'group_by' column is required for groupby."}
        if group_by not in df.columns:
            return {"success": False, "error": f"Column not found: '{group_by}'."}
        try:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if not numeric_cols:
                return {"success": False, "error": "No numeric columns to aggregate."}
            result = df.groupby(group_by)[numeric_cols].agg(["mean", "count", "max", "min"])
            result.columns = ["_".join(c) for c in result.columns]
            result = result.reset_index().to_dict(orient="records")
            result = _convert(result)
            return {"success": True, "operation": "groupby", "group_by": group_by,
                    "shape": shape, "columns": columns, "dtypes": dtypes, "result": result}
        except Exception as e:
            return {"success": False, "error": f"groupby failed: {e}"}

    # ── filter ────────────────────────────────────────────────────────────────
    if operation == "filter":
        if not filter_column:
            return {"success": False, "error": "'filter_column' is required for filter."}
        if filter_column not in df.columns:
            return {"success": False, "error": f"Column not found: '{filter_column}'."}
        try:
            # Attempt numeric cast if column is numeric
            if df[filter_column].dtype in ("int64", "float64"):
                try:
                    filter_value = float(filter_value)
                except (ValueError, TypeError):
                    pass
            filtered = df[df[filter_column] == filter_value]
            rows = _convert(filtered.to_dict(orient="records"))
            return {"success": True, "operation": "filter",
                    "filter_column": filter_column, "filter_value": filter_value,
                    "shape": shape, "columns": columns, "dtypes": dtypes,
                    "matched_rows": len(rows), "result": rows}
        except Exception as e:
            return {"success": False, "error": f"filter failed: {e}"}

    # ── correlation ───────────────────────────────────────────────────────────
    if operation == "correlation":
        try:
            numeric_df = df.select_dtypes(include="number")
            if numeric_df.empty:
                return {"success": False, "error": "No numeric columns for correlation."}
            corr = numeric_df.corr().round(4).to_dict()
            corr = _convert(corr)
            return {"success": True, "operation": "correlation",
                    "shape": shape, "columns": columns, "dtypes": dtypes, "result": corr}
        except Exception as e:
            return {"success": False, "error": f"correlation failed: {e}"}

    # ── value_counts ──────────────────────────────────────────────────────────
    if operation == "value_counts":
        if not column:
            return {"success": False, "error": "'column' is required for value_counts."}
        if column not in df.columns:
            return {"success": False, "error": f"Column not found: '{column}'."}
        try:
            counts = df[column].value_counts().head(int(top_n)).to_dict()
            counts = _convert(counts)
            return {"success": True, "operation": "value_counts", "column": column,
                    "shape": shape, "columns": columns, "dtypes": dtypes, "result": counts}
        except Exception as e:
            return {"success": False, "error": f"value_counts failed: {e}"}

    # ── top_n ─────────────────────────────────────────────────────────────────
    if operation == "top_n":
        try:
            rows = _convert(df.head(int(top_n)).to_dict(orient="records"))
            return {"success": True, "operation": "top_n", "top_n": int(top_n),
                    "shape": shape, "columns": columns, "dtypes": dtypes, "result": rows}
        except Exception as e:
            return {"success": False, "error": f"top_n failed: {e}"}

    return {
        "success": False,
        "error":   f"Unknown operation: '{operation}'. "
                   "Choose from: describe, groupby, filter, correlation, value_counts, top_n.",
    }


# ── Helper: convert numpy types to Python native ──────────────────────────────

def _convert(obj):
    """Recursively convert numpy/pandas types to JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {str(k): _convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert(i) for i in obj]
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    return obj



def execute(args: dict) -> dict:
    return analyze_data(
        source        = args.get("source", ""),
        source_type   = args.get("source_type", "file"),
        operation     = args.get("operation", "describe"),
        column        = args.get("column"),
        group_by      = args.get("group_by"),
        filter_column = args.get("filter_column"),
        filter_value  = args.get("filter_value"),
        top_n         = args.get("top_n", 10),
    )



if __name__ == "__main__":
    import json
    import os

    sample_csv = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample.csv")

    tests = [
        {"source": sample_csv, "operation": "describe"},
        {"source": sample_csv, "operation": "groupby",     "group_by": "course"},
        {"source": sample_csv, "operation": "filter",      "filter_column": "course", "filter_value": "Math"},
        {"source": sample_csv, "operation": "value_counts","column": "course"},
        {"source": sample_csv, "operation": "top_n",       "top_n": 3},
        {"source": sample_csv, "operation": "correlation"},
        {"source": sample_csv, "operation": "unknown_op"},   # error case
    ]

    for t in tests:
        result = execute(t)
        op = t.get("operation", "?")
        if result["success"]:
            print(f"[{op}] shape={result['shape']}  result_type={type(result['result']).__name__}")
        else:
            print(f"[{op}] ERROR: {result['error']}")
        print()
