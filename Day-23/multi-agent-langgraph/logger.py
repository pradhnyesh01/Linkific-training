"""
logger.py
Centralised logging setup for the multi-agent system.

Usage:
    from logger import get_logger
    logger = get_logger("my_module")
    logger.info("Something happened")
    logger.debug("Detailed info")
    logger.error("Something went wrong")

Log levels:
    DEBUG   → file only  (LLM calls, token counts, tool args)
    INFO    → file + console (agent decisions, routing, pipeline steps)
    WARNING → file + console (fallbacks, retries)
    ERROR   → file + console (exceptions, failures)

Log files are written to logs/agent_YYYYMMDD.log (one per day).
"""

import logging
import os
from datetime import datetime

# ── Log directory ──────────────────────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ── Shared formatter ───────────────────────────────────────────────────────────

_FORMATTER = logging.Formatter(
    fmt     = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

# ── Log file (one per day) ─────────────────────────────────────────────────────

_LOG_FILE = os.path.join(LOG_DIR, f"agent_{datetime.now().strftime('%Y%m%d')}.log")


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a named logger.

    Calling get_logger("foo") twice returns the same logger — handlers
    are only added once so logs don't duplicate.

    Args:
        name: Logger name (e.g. "agent.Researcher", "graph", "cost_tracker")

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler — DEBUG and above, all details
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)

    # Console handler — INFO and above, cleaner output
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_FORMATTER)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False   # don't bubble up to root logger

    return logger
