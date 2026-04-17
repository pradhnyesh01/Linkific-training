"""
tools/calculator.py
Tool 1 – Calculator

Performs safe arithmetic without eval().
Supported operations: add, subtract, multiply, divide, power, sqrt, percentage.

Flow: execute(args) → calculate(operation, a, b) → {"success": True/False, ...}
"""

import math
from typing import Any


# ── Core function ─────────────────────────────────────────────────────────────

def calculate(operation: str, a: float, b: float = None) -> dict[str, Any]:
    """
    Perform arithmetic. Always returns a dict — never raises.

    Args:
        operation : one of add / subtract / multiply / divide / power / sqrt / percentage
        a         : first operand
        b         : second operand (not needed for sqrt)

    Returns:
        {"success": True,  "operation": ..., "a": ..., "b": ..., "result": float}
        {"success": False, "error": str}
    """
    operation = operation.strip().lower()

    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"success": False, "error": "Division by zero is undefined."}
            result = a / b
        elif operation == "power":
            result = a ** b
        elif operation == "sqrt":
            if a < 0:
                return {"success": False, "error": "sqrt requires a non-negative number."}
            result = math.sqrt(a)
        elif operation == "percentage":
            # percentage: what is a% of b?
            if b is None:
                return {"success": False, "error": "'b' is required for percentage (a% of b)."}
            result = (a / 100) * b
        else:
            return {"success": False, "error": f"Unknown operation: '{operation}'. "
                    "Choose from: add, subtract, multiply, divide, power, sqrt, percentage."}

        return {
            "success":   True,
            "operation": operation,
            "a":         a,
            "b":         b,
            "result":    round(result, 10),  
        }

    except TypeError as e:
        return {"success": False, "error": f"Type error: {e}. Check that 'a' and 'b' are numbers."}
    except Exception as e:
        return {"success": False, "error": str(e)}



def execute(args: dict) -> dict:
    """
    Entry point for the agent dispatcher.
    Pulls keys from the args dict and calls calculate().
    """
    operation = args.get("operation", "")
    a = args.get("a")
    b = args.get("b")

    if a is None:
        return {"success": False, "error": "'a' is required."}

    return calculate(operation, float(a), float(b) if b is not None else None)



if __name__ == "__main__":
    import json
    tests = [
        {"operation": "add",        "a": 15,   "b": 27},
        {"operation": "subtract",   "a": 100,  "b": 43},
        {"operation": "multiply",   "a": 6,    "b": 7},
        {"operation": "divide",     "a": 22,   "b": 7},
        {"operation": "divide",     "a": 5,    "b": 0},     # error case
        {"operation": "power",      "a": 2,    "b": 10},
        {"operation": "sqrt",       "a": 144},
        {"operation": "sqrt",       "a": -9},               # error case
        {"operation": "percentage", "a": 15,   "b": 847},
        {"operation": "unknown",    "a": 1,    "b": 2},     # error case
    ]
    for t in tests:
        result = execute(t)
        print(json.dumps(result, indent=2))
        print()
