"""
agents/base_agent.py
Base class for all agents in the multi-agent system.

Every agent:
  - Has a name and role description
  - Shares a single OpenAI client
  - Uses _chat() to call the LLM
  - Logs every LLM call (token count, model)
  - Tracks token cost via the global CostTracker
  - Implements run(state) → state
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from openai import OpenAI
from logger import get_logger
from cost_tracker import tracker


class BaseAgent:
    """
    Common foundation for all agents.

    Subclasses must implement:
        run(self, state) -> state
    """

    def __init__(self, name: str, role: str, model: str = "gpt-4o-mini"):
        self.name   = name
        self.role   = role
        self.model  = model
        self.client = OpenAI()
        self.logger = get_logger(f"agent.{name.lower()}")

    # ── LLM helpers ───────────────────────────────────────────────────────────

    def _chat(self, messages: list[dict], tools: list[dict] | None = None) -> str:
        """
        Send messages to OpenAI. Returns the assistant's text response.
        Logs the call and tracks token usage automatically.
        """
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools

        self.logger.debug(f"LLM call — {len(messages)} messages")

        response = self.client.chat.completions.create(**kwargs)
        content  = response.choices[0].message.content or ""

        tracker.track(response, agent_name=self.name)
        self.logger.debug(
            f"LLM response — {response.usage.total_tokens} tokens "
            f"(in={response.usage.prompt_tokens}, out={response.usage.completion_tokens})"
        )

        return content

    def _chat_with_tools(self, messages: list[dict], tools: list[dict], executor) -> tuple[str, list[dict]]:
        """
        Full function-calling loop.

        Keeps calling OpenAI until finish_reason == "stop".
        Each tool call is dispatched via executor(tool_name, args) -> dict.
        Logs every tool call and its result.

        Returns:
            (final_text, tool_calls_made)
        """
        tool_calls_made = []

        while True:
            self.logger.debug(f"LLM call (tool loop) — {len(messages)} messages")

            response      = self.client.chat.completions.create(
                model    = self.model,
                messages = messages,
                tools    = tools,
            )
            choice        = response.choices[0]
            finish_reason = choice.finish_reason
            message       = choice.message

            tracker.track(response, agent_name=self.name)

            if finish_reason == "stop":
                self.logger.debug("Tool loop complete — finish_reason=stop")
                return message.content or "", tool_calls_made

            if finish_reason == "tool_calls":
                messages.append(message)

                for tc in message.tool_calls:
                    fn_name = tc.function.name
                    fn_args = json.loads(tc.function.arguments)

                    self.logger.info(f"Tool call → {fn_name}({fn_args})")
                    result = executor(fn_name, fn_args)
                    self.logger.debug(f"Tool result ← success={result.get('success')}")

                    tool_calls_made.append({"name": fn_name, "args": fn_args, "result": result})
                    messages.append({
                        "role":         "tool",
                        "tool_call_id": tc.id,
                        "content":      json.dumps(result),
                    })
                continue

            self.logger.warning(f"Unexpected finish_reason: {finish_reason}")
            return message.content or "", tool_calls_made

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self, state) -> None:
        raise NotImplementedError(f"{self.name}.run() must be implemented.")
