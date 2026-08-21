"""Voodoo AI Agent starter — an agent with tool calling and a realtime chat UI.

Run:
    voodoo dev          # -> http://localhost:8000

Two providers are wired up (see provider.py):

* ``demo:demo`` — fully offline; performs one deterministic tool call, then
  answers. Used automatically when no API key is set, so the template runs
  with zero setup.

* ``deepseek:<model>`` — a real DeepSeek model served through an
  OpenAI-compatible (LiteLLM) endpoint. Credentials come from ``.env``:

      DEEPSEEK_API_KEY=sk-...
      DEEPSEEK_BASE_URL=https://.../v1
      DEEPSEEK_MODEL=deepseek-v4-flash

  Copy ``.env.example`` to ``.env`` and fill in the key to switch to the live
  model. Point ``DEEPSEEK_BASE_URL`` at any OpenAI-compatible endpoint to use a
  different model provider — no code changes required.

Realtime: mesh events stream agent activity to the browser over the WebSocket
transport — no hand-written JavaScript.
"""

import os

from voodoo import (
    Agent,
    App,
    Badge,
    Button,
    Card,
    Div,
    Heading,
    Input,
    Text,
    event,
    page,
    state,
    tool,
    ws_manager,
)
from dotenv import load_dotenv
from voodoo.ai.providers import register_provider
from voodoo.mesh import mesh
from voodoo.routing.api import api
from voodoo.seo import SEO

# Load .env before reading provider credentials (voodoo also loads it, but we
# make it explicit so the template works when imported standalone).
load_dotenv()

# The MCP SSE handshake returns a StreamingResponse, which the runtime engine
# can't JSON-serialize. Disable run-through-runtime for API routes (the agent
# and pages are unaffected).
api.run_through_runtime = False

app = App()

# Register both providers so they resolve as ``demo:demo`` and ``deepseek:<model>``.
register_provider("demo", "provider.DemoProvider")
register_provider("deepseek", "provider.DeepSeekProvider")

# Pick a real model when a key is present; otherwise fall back to the offline
# demo so the template still runs with zero setup.
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
if os.getenv("DEEPSEEK_API_KEY"):
    MODEL = f"deepseek:{DEEPSEEK_MODEL}"
    MODEL_LABEL = DEEPSEEK_MODEL
    MODEL_SUB = "DeepSeek · tool calling · live"
else:
    MODEL = "demo:demo"
    MODEL_LABEL = "demo:demo"
    MODEL_SUB = "offline · tool calling · zero network"


# ───────────────────────────────────────────────────────────────────────
# 1. Tools — callable by the agent, over MCP, and as plain Python
# ───────────────────────────────────────────────────────────────────────

@tool
async def get_time() -> str:
    """Return the current time."""
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


@tool
async def roll_dice(sides: int = 6) -> int:
    """Roll a die with the given number of sides."""
    import random

    return random.randint(1, sides)


@tool
async def count_words(text: str) -> int:
    """Count the number of words in a string."""
    return len(text.split())


# ───────────────────────────────────────────────────────────────────────
# 2. Agent — demo (offline) or deepseek (from .env)
# ───────────────────────────────────────────────────────────────────────

agent = Agent(
    model=MODEL,
    tools=["get_time", "roll_dice", "count_words"],
    system_prompt=(
        "You are a helpful assistant. Use the available tools when the user "
        "asks for the current time, a random number or dice roll, or a word "
        "count. Otherwise answer directly."
    ),
)


# ───────────────────────────────────────────────────────────────────────
# 3. Realtime — mesh events -> browser log over WebSocket
# ───────────────────────────────────────────────────────────────────────

@mesh.on("agent.started")
async def on_agent_started(payload):
    await ws_manager.broadcast_append(
        "agent-log",
        f'<div class="log-line"><span class="log-dot"></span>run started · {payload["model"]}</div>',
    )


@mesh.on("agent.tool.started")
async def on_tool_started(payload):
    await ws_manager.broadcast_append(
        "agent-log",
        f'<div class="log-line">⚙ tool → {payload["tool"]}</div>',
    )


@mesh.on("agent.completed")
async def on_agent_completed(payload):
    await ws_manager.broadcast_append(
        "agent-log",
        f'<div class="log-line log-line--ok"><span class="log-dot"></span>done · {payload["tokens_out"]} tokens</div>',
    )


# ───────────────────────────────────────────────────────────────────────
# 4. State + events — chat UI
# ───────────────────────────────────────────────────────────────────────

prompt = state("What time is it?")


def _render_output(text: str, meta: str = "", thinking: bool = False) -> str:
    cls = "agent-output thinking" if thinking else "agent-output"
    return Div(
        Text(text, class_="agent-answer"),
        Text(meta, class_="agent-meta"),
        id="agent-output",
        class_=cls,
    ).render()


@page("/")
def home():
    seo = SEO(
        title="Voodoo AI Agent",
        description="An agent with tool calling and a realtime chat UI.",
    )

    ui = Div(
        Div(
            Heading("AI Agent", level=1, class_="page-title"),
            Text(
                "An agent with tool calling and a realtime trace — offline or your own LLM.",
                class_="page-sub",
            ),
            class_="hero",
        ),
        Card(
            Div(
                Badge(MODEL_LABEL),
                Text(MODEL_SUB, class_="muted"),
                class_="chat-head",
            ),
            Div(
                Text("Ask the agent something.", class_="muted"),
                id="agent-output",
                class_="agent-output",
            ),
            Div(id="agent-log", class_="agent-log"),
            Div(
                Input(
                    id="prompt-input",
                    value=prompt.get(),
                    on_change="set_prompt",
                    placeholder="Ask the agent…",
                    class_="chat-input",
                ),
                Button("Run", on_click="run_agent", class_="chat-btn"),
                class_="chat-controls",
            ),
            class_="chat-card",
        ),
        class_="shell",
    )

    return seo, ui


@event
async def set_prompt(element_id, value):
    prompt.set(value)


@event
async def run_agent(element_id, value):
    await ws_manager.broadcast_patch(
        "agent-output", _render_output("Thinking…", thinking=True)
    )
    run = await agent.run(prompt.get())
    meta = (
        f"{run.provider} · {run.tokens_out} tokens · "
        f"{len(run.tool_calls)} tool call(s) · {run.timings['total_ms']:.0f} ms"
    )
    await ws_manager.broadcast_patch("agent-output", _render_output(run.output, meta))


if __name__ == "__main__":
    app.run()
