# Voodoo MCP Server

Expose Python functions to any Model Context Protocol (MCP) client — Claude
Desktop, Cursor, Windsurf, Zed, and more — over a single SSE endpoint. No extra
servers, no boilerplate: a single `@tool` definition is simultaneously a plain
Python function, an AI-agent tool, an MCP tool, and a mesh capability.

## Run

```bash
voodoo dev          # -> http://localhost:8000
```

Open http://localhost:8000 for the tool-registry dashboard, or
http://localhost:8000/demo to call the tools as plain Python.

## Connect an MCP client

The server streams at:

```
http://localhost:8000/mcp/sse
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "voodoo": { "url": "http://localhost:8000/mcp/sse" }
  }
}
```

**Cursor / Windsurf / Zed**: add the same `http://localhost:8000/mcp/sse`
SSE URL in the MCP settings.

## How it works

- `@tool` registers a function in the shared `ToolRegistry`. The MCP server
  (`GET /mcp/sse` + `POST /mcp/messages`) reads that registry, so every
  `@tool` is exposed automatically — no separate registration step.
- `mcp.resource(uri, name)` exposes read-only data over the same endpoint.
- Tools stay callable as plain Python (`add(2, 3)`) — that's exactly what the
  `/demo` page does.

## Gate tools with permissions

Add `permissions=[...]` to require a capability before a tool runs through an
agent or MCP execution context:

```python
@tool(permissions=["kb:read"])
def search_kb(query: str) -> list[str]:
    ...
```

## Project layout

```
main.py              # tools, resources, dashboard + demo pages
voodoo.toml          # app config
.voodoo/theme/       # theme snapshot + bespoke styles
```
