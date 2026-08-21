"""LLM providers for the Voodoo AI Agent template.

Two providers are registered in ``main.py``:

* ``demo:demo`` — fully offline. Performs one deterministic tool call, then
  answers. Used as the fallback so the template runs with zero setup.

* ``deepseek:<model>`` — a real provider that talks to any OpenAI-compatible
  endpoint (here a DeepSeek model served through a LiteLLM gateway). It reads
  its credentials from the environment, loaded from ``.env``:

      DEEPSEEK_API_KEY=sk-...
      DEEPSEEK_BASE_URL=https://.../v1
      DEEPSEEK_MODEL=deepseek/deepseek-v4-flash-0731

Both walk the same tool-call loop: the provider returns a ``[TOOL: name]``
request, the agent executes the tool through the shared registry, and the
provider then composes the final answer.
"""

from __future__ import annotations

import os
import platform
import sys
from collections.abc import AsyncIterator
from typing import Any

from voodoo.ai.providers import (
    LLMProvider,
    Message,
    ModelDescriptor,
    ProviderEvent,
    ProviderResponse,
)
from voodoo.ai.providers.mock import MockProvider
from voodoo.core.errors import ConfigurationError

__all__ = ["DemoProvider", "DeepSeekProvider"]


def _patch_macos_version() -> None:
    """Work around a ``truststore`` crash on macOS 26 (Darwin 25+).

    On some CPython builds ``platform.mac_ver()[0]`` returns an empty string
    (the macOS 26 / Darwin 25 release plumbing changed). ``truststore`` — which
    the ``openai`` SDK pulls in via ``httpcore2`` / ``httpx2`` — calls
    ``int(platform.mac_ver()[0].split(".")[0])`` at import time and raises
    ``ValueError`` on the empty value, which makes ``openai.AsyncOpenAI(...)``
    impossible to construct.

    ``truststore`` only uses that value to pick a CDLL path and to enforce a
    ``>= (10, 14)`` minimum, so feeding it a real release string is safe. We do
    it here (once, at import time) so every OpenAI client in this process is
    unblocked.
    """
    if sys.platform != "darwin":
        return
    if platform.mac_ver()[0]:
        return  # healthy environment — nothing to patch

    release = platform.release() or "14.0"

    def _mac_ver() -> tuple[str, tuple[str, str, str], str]:
        return (release, ("", "", ""), platform.machine())

    platform.mac_ver = _mac_ver


_patch_macos_version()


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


def _to_openai_tools(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Convert the agent's flat tool specs into OpenAI function-call form."""
    if not tools:
        return []
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get(
                    "input_schema", {"type": "object", "properties": {}}
                ),
            },
        }
        for t in tools
    ]


def _first_tool_call(msg: Any) -> tuple[str, str] | None:
    """Pull ``(name, arguments_json)`` from a native OpenAI tool-call message."""
    tool_calls = getattr(msg, "tool_calls", None)
    if not tool_calls:
        return None
    tc = tool_calls[0]
    fn = getattr(tc, "function", None)
    if fn is None and isinstance(tc, dict):
        fn = tc.get("function", {})
    if fn is None:
        return None
    name = getattr(fn, "name", None)
    if name is None and isinstance(fn, dict):
        name = fn.get("name", "")
    arguments = getattr(fn, "arguments", None)
    if arguments is None and isinstance(fn, dict):
        arguments = fn.get("arguments", "{}")
    return (name or "", arguments or "{}")


class DeepSeekProvider(LLMProvider):
    """OpenAI-compatible provider for DeepSeek (via a LiteLLM gateway).

    Reads ``DEEPSEEK_API_KEY``, ``DEEPSEEK_BASE_URL`` and ``DEEPSEEK_MODEL``
    from the environment (see ``.env.example``). Native tool calls are
    translated into the agent's ``[TOOL: ...]`` convention so the existing
    loop executes them through the shared registry.
    """

    name = "deepseek"

    def __init__(
        self, model: str = "deepseek/deepseek-v4-flash-0731", **kwargs: Any
    ) -> None:
        super().__init__(model, **kwargs)
        try:
            import openai
        except ImportError as exc:  # pragma: no cover - exercised without SDK
            raise ConfigurationError(
                "The 'openai' package is required for the deepseek provider. "
                "Install it with: pip install openai"
            ) from exc

        api_key = kwargs.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        base_url = kwargs.get("base_url") or os.getenv("DEEPSEEK_BASE_URL")
        if not api_key:
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is not set. Add it to .env "
                "(see .env.example) or pass api_key=... to Agent(...)."
            )
        self._client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def _normalize_messages(messages: list[Message]) -> list[Message]:
        """Rewrite the agent's marker/tool messages into a clean transcript.

        The agent records the tool request as an assistant message containing
        ``[TOOL: ...]`` and the result as a ``tool`` role message. Native
        OpenAI-compatible backends expect either real tool-call objects or
        plain text, so we drop the synthetic marker and surface the result as
        an observation the model can answer from.
        """
        cleaned: list[Message] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "assistant" and "[TOOL:" in str(content):
                continue  # drop the synthetic tool-request marker
            if role == "tool":
                cleaned.append(
                    {
                        "role": "user",
                        "content": (
                            f"[tool result] {msg.get('name', 'tool')}: {content}"
                        ),
                    }
                )
                continue
            cleaned.append(msg)
        return cleaned

    async def complete(
        self, messages: list[Message], **kwargs: Any
    ) -> ProviderResponse:
        request: dict[str, Any] = {
            "model": self.model,
            "messages": self._normalize_messages(messages),
        }
        tools = _to_openai_tools(kwargs.get("tools"))
        if tools:
            request["tools"] = tools

        resp = await self._client.chat.completions.create(**request)
        choice = resp.choices[0]
        msg = choice.message
        usage = getattr(resp, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage else 0

        tool_call = _first_tool_call(msg)
        if tool_call:
            name, arguments = tool_call
            content = f"[TOOL: {name}] args: {arguments}"
        else:
            content = msg.content or ""

        return ProviderResponse(
            content=content,
            model=getattr(resp, "model", None) or self.model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=0.0,
            finish_reason=getattr(choice, "finish_reason", None) or "stop",
        )

    async def stream(
        self, messages: list[Message], **kwargs: Any
    ) -> AsyncIterator[ProviderEvent]:
        request: dict[str, Any] = {
            "model": self.model,
            "messages": self._normalize_messages(messages),
            "stream": True,
        }
        tools = _to_openai_tools(kwargs.get("tools"))
        if tools:
            request["tools"] = tools

        stream = await self._client.chat.completions.create(**request)
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield ProviderEvent(
                    type="text",
                    data={"text": chunk.choices[0].delta.content},
                )
        yield ProviderEvent(
            type="done",
            data={"model": self.model, "finish_reason": "stop"},
        )

    def describe(self) -> ModelDescriptor:
        return ModelDescriptor(
            provider=self.name,
            model=self.model,
            modalities=["text"],
            context_window=128000,
            tool_use=True,
            structured_output=False,
            streaming=True,
            reasoning=False,
            vision=False,
            audio=False,
            embeddings=False,
        )
