# Voodoo AI Agent

An AI agent with tool calling, streaming, and a realtime trace — all rendered
from Python, no hand-written JavaScript. Ships with an offline `demo:demo`
provider that deterministically performs a real tool call, so you can see the
full loop with zero API keys.

## Run

```bash
voodoo dev          # -> http://localhost:8000
```

Open http://localhost:8000 and click **Run**. The agent calls `get_time`, then
composes a final answer from the tool result — and its activity streams into
the browser log in realtime over the WebSocket transport.

## How it works

- `@tool` registers `get_time`, `roll_dice`, and `count_words` in the shared
  `ToolRegistry`. The agent gets them by name via `tools=[...]`.
- `provider.py` defines `DemoProvider`, an offline provider that first returns
  a `[TOOL: get_time]` request and then answers from the tool result.
  `register_provider("demo", "provider.DemoProvider")` makes it resolvable as
  `demo:demo`.
- `Agent(model="demo:demo", ...)` runs the tool-call loop with no network.
- Mesh events (`agent.started`, `agent.tool.started`, `agent.completed`) are
  handled with `@mesh.on(...)` and pushed to the browser with
  `ws_manager.broadcast_append(...)`.
- The final answer is patched into the DOM with
  `ws_manager.broadcast_patch(...)` after `await agent.run(...)`.

## Swap in a real model

Set the relevant provider key, change the model string, and drop the
`register_provider(...)` line:

```python
agent = Agent(
    model="openai:gpt-4o",
    tools=["get_time", "roll_dice", "count_words"],
    system_prompt="You are a helpful assistant.",
)
```

Supported providers include `openai:*`, `anthropic:*`, `mock:*`, and the
bundled `demo:*`. See the framework docs for the full list and env-var names.

## Stream tokens as they arrive

Replace `agent.run(...)` with `agent.stream(...)` and patch the output for each
`text` event to get a word-by-word typewriter effect.

## Project layout

```
main.py              # tools, agent, mesh handlers, chat UI
provider.py          # offline demo provider (tool-call loop)
voodoo.toml          # app config
.voodoo/theme/       # theme snapshot + bespoke styles
```
