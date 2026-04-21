"""
agents/base_agent.py
Base class for all agents in the multi-agent system.

Every agent:
  - Has a name and role description
  - Shares a single OpenAI client
  - Uses _chat() to call the LLM
  - Implements run(state) → state
"""

import json
from openai import OpenAI
from state import ResearchState


class BaseAgent:
    """
    Common foundation for all agents.

    Subclasses must implement:
        run(self, state: ResearchState) -> ResearchState
    """

    def __init__(self, name: str, role: str, model: str = "gpt-4o-mini"):
        self.name   = name
        self.role   = role
        self.model  = model
        self.client = OpenAI()   # reads OPENAI_API_KEY from environment

    # ── LLM helpers ───────────────────────────────────────────────────────────

    def _chat(self, messages: list[dict], tools: list[dict] | None = None) -> str:
        """
        Send messages to OpenAI. Returns the assistant's text response.
        If tools are provided, they are passed as function-calling schemas.
        """
        kwargs = {
            "model":    self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        content  = response.choices[0].message.content
        return content or ""

    def _chat_with_tools(self, messages: list[dict], tools: list[dict], executor) -> tuple[str, list[dict]]:
        """
        Full function-calling loop.

        Keeps calling OpenAI until finish_reason == "stop".
        Each tool call is dispatched via executor(tool_name, args) -> dict.

        Returns:
            (final_text, tool_calls_made)
            where tool_calls_made is a list of {name, args, result}
        """
        tool_calls_made = []

        while True:
            response      = self.client.chat.completions.create(
                model    = self.model,
                messages = messages,
                tools    = tools,
            )
            choice        = response.choices[0]
            finish_reason = choice.finish_reason
            message       = choice.message

            if finish_reason == "stop":
                return message.content or "", tool_calls_made

            if finish_reason == "tool_calls":
                # Append the assistant's tool_calls message first
                messages.append(message)

                # Execute each requested tool call
                for tc in message.tool_calls:
                    fn_name = tc.function.name
                    fn_args = json.loads(tc.function.arguments)

                    result = executor(fn_name, fn_args)
                    tool_calls_made.append({"name": fn_name, "args": fn_args, "result": result})

                    # Append tool result message
                    messages.append({
                        "role":         "tool",
                        "tool_call_id": tc.id,
                        "content":      json.dumps(result),
                    })
                # Loop back — send updated messages to get next response
                continue

            # Unexpected finish reason — stop safely
            return message.content or "", tool_calls_made

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self, state: ResearchState) -> ResearchState:
        raise NotImplementedError(f"{self.name}.run() must be implemented.")
