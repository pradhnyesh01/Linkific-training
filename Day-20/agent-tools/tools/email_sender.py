"""
tools/email_sender.py
Tool 6 – Email Sender (Simulation)

No real SMTP is used. This tool:
  1. Validates the recipient email address format.
  2. Generates a fake message ID.
  3. Logs the simulated email to logs/email_log.txt.
  4. Prints a confirmation to the console.

Flow: execute(args) → send_email(...) → {"success": True/False, ...}
"""

import os
import re
import json
from datetime import datetime
from typing import Any

# Resolve log file relative to this file's location
_LOGS_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
_LOG_FILE  = os.path.join(_LOGS_DIR, "email_log.txt")

_EMAIL_RE  = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# ── Core function ─────────────────────────────────────────────────────────────

def send_email(
    to:       str,
    subject:  str,
    body:     str,
    cc:       str  = None,
    priority: str  = "normal",
) -> dict[str, Any]:
    """
    Simulate sending an email.

    Args:
        to       : recipient email address
        subject  : email subject line
        body     : email body text
        cc       : optional CC address
        priority : "low", "normal", or "high"

    Returns:
        {"success": True,  "message_id": str, "timestamp": str, ...}
        {"success": False, "error": str}
    """
    # ── Validation ────────────────────────────────────────────────────────────
    if not to or not _EMAIL_RE.match(to.strip()):
        return {"success": False, "error": f"Invalid email address: '{to}'."}
    if cc and not _EMAIL_RE.match(cc.strip()):
        return {"success": False, "error": f"Invalid CC email address: '{cc}'."}
    if not subject or not subject.strip():
        return {"success": False, "error": "Subject cannot be empty."}
    if not body or not body.strip():
        return {"success": False, "error": "Body cannot be empty."}
    if priority not in ("low", "normal", "high"):
        priority = "normal"

    # ── Build log entry ───────────────────────────────────────────────────────
    timestamp  = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    message_id = f"MSG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{abs(hash(to)) % 10000:04d}"

    log_entry = {
        "message_id": message_id,
        "timestamp":  timestamp,
        "to":         to.strip(),
        "cc":         cc.strip() if cc else None,
        "subject":    subject.strip(),
        "priority":   priority,
        "body_chars": len(body),
    }

    # ── Write to log file ─────────────────────────────────────────────────────
    os.makedirs(_LOGS_DIR, exist_ok=True)
    with open(_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # ── Console output ────────────────────────────────────────────────────────
    priority_icons = {"low": "📌", "normal": "📧", "high": "🚨"}
    icon = priority_icons.get(priority, "📧")
    print(f"\n{icon} [EMAIL SIMULATED]")
    print(f"   To      : {to}")
    if cc:
        print(f"   CC      : {cc}")
    print(f"   Subject : {subject}")
    print(f"   Priority: {priority.upper()}")
    print(f"   ID      : {message_id}")
    print(f"   Logged  : {_LOG_FILE}\n")

    return {
        "success":    True,
        "simulated":  True,
        "message_id": message_id,
        "to":         to.strip(),
        "cc":         cc.strip() if cc else None,
        "subject":    subject.strip(),
        "priority":   priority,
        "timestamp":  timestamp,
        "logged_to":  os.path.abspath(_LOG_FILE),
    }


# ── Unified entry point ───────────────────────────────────────────────────────

def execute(args: dict) -> dict:
    return send_email(
        to       = args.get("to", ""),
        subject  = args.get("subject", ""),
        body     = args.get("body", ""),
        cc       = args.get("cc"),
        priority = args.get("priority", "normal"),
    )


# ── Quick self-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json as _json

    tests = [
        {   # Normal email
            "to": "alice@example.com",
            "subject": "Project Update",
            "body": "Hi Alice, the project is on track for the Friday deadline.",
        },
        {   # High priority with CC
            "to": "manager@company.com",
            "subject": "URGENT: Server Down",
            "body": "Production server is unreachable. Investigating now.",
            "cc": "devops@company.com",
            "priority": "high",
        },
        {   # Error: bad email
            "to": "not-an-email",
            "subject": "Test",
            "body": "Body",
        },
        {   # Error: empty subject
            "to": "valid@email.com",
            "subject": "",
            "body": "Body",
        },
    ]

    for t in tests:
        result = execute(t)
        print(_json.dumps(result, indent=2))
        print()
