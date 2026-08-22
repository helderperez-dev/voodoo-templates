"""The offline demo provider.

``demo:demo`` performs one deterministic tool call (``get_time``), then
composes a final answer from the tool result — so the template runs with zero
setup and no network. Used automatically when no API key is set.
"""

from __future__ import annotations

from typing import Any

from voodoo.ai.providers import (
    Message,
    ModelDescriptor,
    ProviderResponse,
)
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
