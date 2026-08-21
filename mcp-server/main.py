"""Voodoo MCP Server starter.

Expose Python functions to any Model Context Protocol (MCP) client — Claude
Desktop, Cursor, Windsurf, Zed, and more — over a single SSE endpoint. No extra
servers, no boilerplate: one ``@tool`` definition is simultaneously a plain
Python function, an AI-agent tool, an MCP tool, and a mesh capability.

Run:
    voodoo dev                 # -> http://localhost:8000
    curl -N http://localhost:8000/mcp/sse

Connect (Claude Desktop ``claude_desktop_config.json``):

    {
      "mcpServers": {
        "voodoo": { "url": "http://localhost:8000/mcp/sse" }
      }
    }
"""

import json

from voodoo import (
    A,
    App,
    Badge,
    Card,
    CodeBlock,
    Div,
    Heading,
    Text,
    page,
    tool,
)
from voodoo.ai.tools import default_registry
from voodoo.mcp import mcp
from voodoo.routing.api import api
from voodoo.seo import SEO

# The MCP SSE handshake returns a StreamingResponse. In voodoo 1.18.0 every
# API handler runs through the runtime engine, which persists the Execution
# result with ``model_dump(mode="json")`` — pydantic can't serialize a
# StreamingResponse, so ``/mcp/sse`` would 500. Bypass the runtime engine for
# API routes: the MCP ``tools/call`` path still works exactly the same.
api.run_through_runtime = False

app = App()


# ───────────────────────────────────────────────────────────────────────
# 1. Tools — one definition, four consumers:
#    plain Python · Agent · MCP · Mesh
# ───────────────────────────────────────────────────────────────────────

@tool(description="Add two numbers and return the sum.")
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool
def get_time() -> str:
    """Return the current server time (ISO 8601)."""
    from datetime import datetime

    return datetime.now().isoformat(timespec="seconds")


@tool
def search_kb(query: str, limit: int = 5) -> list[str]:
    """Search the built-in knowledge base for a query."""
    kb = [
        "Voodoo is one runtime for web, APIs, agents, and events.",
        "MCP lets AI IDEs call your Python tools over SSE.",
        "A @tool definition serves Python, agents, MCP, and mesh.",
        "The mock provider runs agents with zero API keys.",
        "Mesh is a local-first, realtime event bus.",
    ]
    q = query.lower()
    return [item for item in kb if q in item.lower()][:limit]


@tool
def echo(message: str) -> str:
    """Echo a message back unchanged."""
    return message


# ───────────────────────────────────────────────────────────────────────
# 2. Resources — read-only data exposed to MCP clients
# ───────────────────────────────────────────────────────────────────────

@mcp.resource("kb://about", name="About")
def about_resource() -> str:
    """A short description of this template."""
    return "Voodoo MCP starter: tools + resources over a single SSE endpoint."


@mcp.resource("system://status", name="Status")
def status_resource() -> str:
    """Server status line."""
    return "ok"


# ───────────────────────────────────────────────────────────────────────
# 3. Pages — a registry dashboard and a plain-Python demo
# ───────────────────────────────────────────────────────────────────────

def _tool_card(spec) -> Card:
    return Card(
        Div(
            Badge(spec.name),
            Text(spec.description or "No description.", class_="tool-desc"),
            class_="tool-head",
        ),
        CodeBlock(json.dumps(spec.input_schema, indent=2), language="json"),
        class_="tool-card",
    )


@page("/")
def home():
    tools = default_registry.all()
    resources = mcp.resources

    seo = SEO(
        title="Voodoo MCP Server",
        description="Expose Python tools to any MCP client over a single SSE endpoint.",
    )

    ui = Div(
        Div(
            Heading("MCP Server", level=1, class_="page-title"),
            Text("One endpoint. Every AI IDE. Zero boilerplate.", class_="page-sub"),
            class_="hero",
        ),
        Card(
            Heading("Connect", level=2),
            Text("Stream your tools to any MCP client:", class_="muted"),
            CodeBlock("http://localhost:8000/mcp/sse", language="text"),
            Text("Claude Desktop config:", class_="muted"),
            CodeBlock(
                '{\n  "mcpServers": {\n    "voodoo": { "url": "http://localhost:8000/mcp/sse" }\n  }\n}',
                language="json",
            ),
        ),
        Card(
            Heading(f"{len(tools)} tools", level=2),
            Text(
                "Registered via @tool — callable as Python, by agents, and over MCP.",
                class_="muted",
            ),
            Div(*[_tool_card(s) for s in tools], class_="tool-grid"),
        ),
        Card(
            Heading(f"{len(resources)} resources", level=2),
            Div(
                *[
                    Div(Badge(uri), Text(res["name"], class_="muted"), class_="resource-row")
                    for uri, res in resources.items()
                ],
                class_="resource-list",
            ),
        ),
        Card(
            Heading("Try it", level=2),
            Text(
                "Tools stay plain Python — call them directly, or visit the demo.",
                class_="muted",
            ),
            A("Run the demo", href="/demo", class_="hero-link hero-link--solid"),
        ),
        class_="shell",
    )

    return seo, ui


@page("/demo")
def demo():
    seo = SEO(title="MCP Server — demo")

    samples = [
        ("add(2, 3)", add(2, 3)),
        ("get_time()", get_time()),
        ("search_kb('MCP')", search_kb("MCP")),
        ("echo('hello')", echo("hello")),
    ]

    ui = Div(
        Div(
            Heading("Tool demo", level=1, class_="page-title"),
            Text(
                "The same functions an MCP client calls, invoked as plain Python.",
                class_="page-sub",
            ),
            class_="hero",
        ),
        Card(
            Div(
                *[
                    Div(Badge(label), Text(str(value), class_="muted"), class_="resource-row")
                    for label, value in samples
                ],
                class_="resource-list",
            )
        ),
        A("← Back", href="/", class_="hero-link"),
        class_="shell",
    )

    return seo, ui


if __name__ == "__main__":
    app.run()
