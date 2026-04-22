"""
cost_tracker.py
Tracks OpenAI API token usage and estimates costs across all agent calls.

Usage:
    from cost_tracker import tracker          # import the global singleton

    # Inside an agent after an API call:
    tracker.track(response, agent_name="Researcher")

    # At the end of a run:
    tracker.summary()
    tracker.reset()   # clear for next run

Pricing (as of 2024, gpt-4o-mini):
    Input  tokens: $0.150 per 1M tokens
    Output tokens: $0.600 per 1M tokens
"""

from dataclasses import dataclass, field
from logger import get_logger

logger = get_logger("cost_tracker")

# ── Pricing table (USD per token) ─────────────────────────────────────────────

PRICING = {
    "gpt-4o-mini": {
        "input":  0.150 / 1_000_000,
        "output": 0.600 / 1_000_000,
    },
    "gpt-4o": {
        "input":  5.00  / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
}

DEFAULT_MODEL = "gpt-4o-mini"


# ── CostTracker class ─────────────────────────────────────────────────────────

@dataclass
class CostTracker:
    """
    Accumulates token usage across all LLM calls in a pipeline run.
    Use the module-level `tracker` singleton — don't create new instances.
    """
    calls:         int   = 0
    input_tokens:  int   = 0
    output_tokens: int   = 0
    total_cost:    float = 0.0
    _calls_log:    list  = field(default_factory=list)

    def track(self, response, agent_name: str = "unknown"):
        """
        Record token usage from an OpenAI API response.

        Args:
            response:   The openai.ChatCompletion response object.
            agent_name: Which agent made the call (for breakdown reporting).
        """
        usage = getattr(response, "usage", None)
        if not usage:
            logger.warning(f"No usage data in response from {agent_name}")
            return

        model  = getattr(response, "model", DEFAULT_MODEL)
        prices = PRICING.get(model, PRICING[DEFAULT_MODEL])

        input_t  = usage.prompt_tokens
        output_t = usage.completion_tokens
        cost     = (input_t * prices["input"]) + (output_t * prices["output"])

        self.calls         += 1
        self.input_tokens  += input_t
        self.output_tokens += output_t
        self.total_cost    += cost

        entry = {
            "agent":         agent_name,
            "model":         model,
            "input_tokens":  input_t,
            "output_tokens": output_t,
            "cost_usd":      round(cost, 6),
        }
        self._calls_log.append(entry)

        logger.debug(
            f"[{agent_name}] {model} — "
            f"in={input_t} out={output_t} tokens — "
            f"${cost:.6f}"
        )

    def summary(self):
        """Print a formatted cost and token usage summary."""
        total_tokens = self.input_tokens + self.output_tokens

        print(f"\n{'='*52}", flush=True)
        print("  Cost Tracking Summary", flush=True)
        print(f"{'='*52}", flush=True)
        print(f"  Total API calls  : {self.calls}", flush=True)
        print(f"  Input tokens     : {self.input_tokens:,}", flush=True)
        print(f"  Output tokens    : {self.output_tokens:,}", flush=True)
        print(f"  Total tokens     : {total_tokens:,}", flush=True)
        print(f"  Estimated cost   : ${self.total_cost:.4f} USD", flush=True)

        if self._calls_log:
            print(f"\n  Per-agent breakdown:", flush=True)
            by_agent: dict = {}
            for call in self._calls_log:
                a = call["agent"]
                if a not in by_agent:
                    by_agent[a] = {"calls": 0, "tokens": 0, "cost": 0.0}
                by_agent[a]["calls"]  += 1
                by_agent[a]["tokens"] += call["input_tokens"] + call["output_tokens"]
                by_agent[a]["cost"]   += call["cost_usd"]

            for agent, stats in by_agent.items():
                print(
                    f"    {agent:<15}  "
                    f"{stats['calls']} call(s)  "
                    f"{stats['tokens']:>6,} tokens  "
                    f"${stats['cost']:.4f}",
                    flush=True,
                )

        print(f"{'='*52}\n", flush=True)
        logger.info(
            f"Run complete — {self.calls} calls, "
            f"{total_tokens:,} tokens, ${self.total_cost:.4f}"
        )

    def reset(self):
        """Clear all accumulated data (call between runs)."""
        self.calls         = 0
        self.input_tokens  = 0
        self.output_tokens = 0
        self.total_cost    = 0.0
        self._calls_log    = []


# ── Global singleton ──────────────────────────────────────────────────────────
# Import this everywhere: from cost_tracker import tracker

tracker = CostTracker()
