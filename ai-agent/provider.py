"""Offline demo provider for the Voodoo AI Agent template.

The built-in ``mock:test`` provider is great for plain completions, but it
never requests a tool — so a template built only on it can't show the tool
calling loop. This small provider walks that loop deterministically:

    1. First response  -> ``[TOOL: get_time]`` (asks the agent to call a tool)
    2. After the result -> a final answer that quotes the tool result

No network, no API keys. To use a real model, change the ``Agent`` model
string in ``main.py`` (e.g. ``"openai:gpt-4o-mini"`` or ``"anthropic:..."``)
and delete the ``register_provider`` line.
"""

from __future__ import annotations

from typing import Any

from voodoo.ai.providers import Message, ModelDescriptor, ProviderResponse
from voodoo.ai.providers.mock import MockProvider

__all__ = ["DemoProvider"]


def _word_count(text: str) -> int:
    return len(str(text).split())


class DemoProvider(MockProvider):
    """Deterministic provider that performs one tool call, then answers."""

    name = "demo"

    async def complete(
        self, messages: list[Message], **kwargs: Any
    ) -> ProviderResponse:
        # Once a tool result is present, compose the final answer from it.
        for msg in reversed(messages):
            if msg.get("role") == "tool":
                result = msg.get("content", "")
                content = f"The tool returned: {result}. Here is your answer."
                break
        else:
            # No tool result yet — ask the agent to call ``get_time``.
            content = "[TOOL: get_time]"

        tokens_in = sum(_word_count(m.get("content", "")) for m in messages)
        return ProviderResponse(
            content=content,
            model=self.model,
            tokens_in=tokens_in,
            tokens_out=_word_count(content),
            cost=0.0,
            finish_reason="stop",
        )

    def describe(self) -> ModelDescriptor:
        """Advertise tool use so introspection reflects reality."""
        return ModelDescriptor(
            provider=self.name,
            model=self.model,
            modalities=["text"],
            context_window=8192,
            tool_use=True,
            structured_output=False,
            streaming=False,
            reasoning=False,
            vision=False,
            audio=False,
            embeddings=False,
        )
