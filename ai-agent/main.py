"""Voodoo AI Agent starter — an agent with tool calling and a realtime chat UI.

Run:
    voodoo dev          # -> http://localhost:8000

Uses an offline ``demo:demo`` provider (see provider.py) that deterministically
performs one tool call, then answers — no network, no API keys. To use a real
model once you have keys, swap the model string and drop the register call:

    agent = Agent(model="openai:gpt-4o", tools=[...])
    agent = Agent(model="anthropic:claude-3-opus", tools=[...])

Realtime: mesh events stream agent activity to the browser over the WebSocket
transport — no hand-written JavaScript.
"""

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
from voodoo.ai.providers import register_provider
from voodoo.mesh import mesh
from voodoo.routing.api import api
from voodoo.seo import SEO

# The MCP SSE handshake returns a StreamingResponse, which the runtime engine
# can't JSON-serialize. Disable run-through-runtime for API routes (the agent
# and pages are unaffected).
api.run_through_runtime = False

app = App()

# Register the offline demo provider under the ``demo`` prefix so the Agent can
# resolve ``demo:demo``. Remove this line when switching to a real provider.
register_provider("demo", "provider.DemoProvider")


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
# 2. Agent — offline demo provider (deterministic, zero keys)
# ───────────────────────────────────────────────────────────────────────

agent = Agent(
    model="demo:demo",
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
                "An agent with tool calling and a realtime trace — no API keys needed.",
                class_="page-sub",
            ),
            class_="hero",
        ),
        Card(
            Div(
                Badge("demo:demo"),
                Text("offline · tool calling · zero network", class_="muted"),
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
