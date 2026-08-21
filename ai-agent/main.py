"""Voodoo AI Agent starter — an agent with tool calling and a realtime chat UI.

Run:
    voodoo dev          # -> http://localhost:8000

Project layout:

    main.py        entry point: loads .env, registers providers, boots the app
    tools.py       the ``@tool`` functions the agent can call
    agent.py       the Agent (demo or deepseek) + realtime mesh handlers
    provider.py    DemoProvider + DeepSeekProvider (see provider.py)
    app/page.py    the chat page (folder-based routing)

Two providers are wired up (see provider.py):

* ``demo:demo`` — fully offline; performs one deterministic tool call, then
  answers. Used automatically when no API key is set, so the template runs
  with zero setup.

* ``deepseek:<model>`` — a real DeepSeek model served through an
  OpenAI-compatible (LiteLLM) endpoint. Credentials come from ``.env``:

      DEEPSEEK_API_KEY=sk-...
      DEEPSEEK_BASE_URL=https://.../v1
      DEEPSEEK_MODEL=deepseek-v4-flash

Realtime: mesh events stream agent activity to the browser over the WebSocket
transport — no hand-written JavaScript.
"""

from pathlib import Path

from dotenv import load_dotenv
from voodoo import App
from voodoo.ai.providers import register_provider
from voodoo.routing.api import api

# Load .env before reading provider credentials (voodoo also loads it, but we
# make it explicit so the template works when imported standalone). Anchor the
# path to this file so it resolves regardless of the process working directory.
load_dotenv(Path(__file__).resolve().with_name(".env"))

# The MCP SSE handshake returns a StreamingResponse, which the runtime engine
# can't JSON-serialize. Disable run-through-runtime for API routes (the agent
# and pages are unaffected).
api.run_through_runtime = False

app = App()

# Register both providers so they resolve as ``demo:demo`` and ``deepseek:<model>``.
register_provider("demo", "provider.DemoProvider")
register_provider("deepseek", "provider.DeepSeekProvider")

# Import the agent module, which pulls in the tools (``tools.py``) and
# registers the realtime mesh handlers. The chat page lives in ``app/page.py``
# and is discovered automatically by folder-based routing.
import agent  # noqa: E402, F401


if __name__ == "__main__":
    app.run()
