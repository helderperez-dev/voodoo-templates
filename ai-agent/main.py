"""Voodoo AI Agent starter — an agent with tool calling and a realtime chat UI.

Run:
    voodoo dev          # -> http://localhost:8000

Project layout:

    main.py              entry point: loads .env, boots the app
    app/                 the application package
      page.py            the chat page (folder-based routing -> /)
      ai/                the AI layer
        agent.py         the Agent + realtime mesh handlers
        tools.py         the ``@tool`` functions the agent can call
        providers/       one module per model provider
          deepseek.py    the live OpenAI-compatible provider

The agent runs on ``deepseek:<model>`` — a real DeepSeek model served through
an OpenAI-compatible (LiteLLM) endpoint. Credentials come from ``.env``:

      DEEPSEEK_API_KEY=sk-...
      DEEPSEEK_BASE_URL=https://.../v1
      DEEPSEEK_MODEL=deepseek-v4-flash

Realtime: mesh events stream agent activity to the browser over the WebSocket
transport — no hand-written JavaScript.
"""

from pathlib import Path

from dotenv import load_dotenv
from voodoo import App
from voodoo.routing.api import api

# Load .env before reading provider credentials (voodoo also loads it, but we
# make it explicit so the template works when imported standalone). Anchor the
# path to this file so it resolves regardless of the process working directory.
load_dotenv(Path(__file__).resolve().with_name(".env"))

# The MCP SSE handshake returns a StreamingResponse, which the runtime engine
# can't JSON-serialize. Disable run-through-runtime for API routes (the agent
# and pages are unaffected).
api.run_through_runtime = False

# Import the AI layer: ``app.ai.providers`` registers the model providers,
# ``app.ai.agent`` builds the Agent + realtime mesh handlers (and pulls in
# ``app.ai.tools``). The chat page lives in ``app/page.py`` and is discovered
# automatically by folder-based routing.
#
# NOTE: these ``import app.*`` statements bind the name ``app`` to the
# *package*, so they must come BEFORE ``app = App()`` — otherwise the ASGI app
# object (exported as ``main:app`` for ``voodoo dev``) would be shadowed by
# the package module.
import app.ai.providers  # noqa: E402, F401
import app.ai.agent  # noqa: E402, F401

app = App()


if __name__ == "__main__":
    app.run()
