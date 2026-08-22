"""Home page — the chat UI.

Folder-based routing: ``app/page.py`` maps to ``/``. The ``page(request)``
function returns an ``(SEO, Component)`` tuple; ``@event`` handlers wire the
input/button to the agent and patch the DOM over the WebSocket transport.
"""

from voodoo import (
    Badge,
    Button,
    Card,
    Div,
    Heading,
    Input,
    Text,
    event,
    state,
    ws_manager,
)
from voodoo.seo import SEO

from app.ai.agent import MODEL_LABEL, MODEL_SUB, agent

prompt = state("What time is it?")


def _render_output(text: str, meta: str = "", thinking: bool = False) -> str:
    cls = "agent-output thinking" if thinking else "agent-output"
    return Div(
        Text(text, class_="agent-answer"),
        Text(meta, class_="agent-meta"),
        id="agent-output",
        class_=cls,
    ).render()


def page(request):
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
