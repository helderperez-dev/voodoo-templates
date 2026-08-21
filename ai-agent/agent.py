"""Agent setup — model selection, the ``Agent`` instance, and realtime logging.

Picks a live ``deepseek:<model>`` when ``DEEPSEEK_API_KEY`` is set in ``.env``,
otherwise falls back to the offline ``demo:demo`` provider.

Mesh handlers below stream agent activity to the browser log over the
WebSocket transport (``ws_manager``).
"""

import os

from voodoo import Agent, ws_manager
from voodoo.mesh import mesh

import tools  # noqa: F401  (imported for its @tool registrations)

__all__ = ["agent", "MODEL", "MODEL_LABEL", "MODEL_SUB"]

DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
if os.getenv("DEEPSEEK_API_KEY"):
    MODEL = f"deepseek:{DEEPSEEK_MODEL}"
    MODEL_LABEL = DEEPSEEK_MODEL
    MODEL_SUB = "DeepSeek · tool calling · live"
else:
    MODEL = "demo:demo"
    MODEL_LABEL = "demo:demo"
    MODEL_SUB = "offline · tool calling · zero network"


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
# Realtime — mesh events -> browser log over WebSocket
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
