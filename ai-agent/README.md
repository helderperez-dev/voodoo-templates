# Voodoo AI Agent

An AI agent with tool calling, streaming, and a realtime trace — all rendered
from Python, no hand-written JavaScript.

It ships with **two providers** and picks automatically:

- **`deepseek:<model>`** — a real model served through an OpenAI-compatible
  (LiteLLM) endpoint. Used when a key is present in `.env`.
- **`demo:demo`** — fully offline, deterministically performs one real tool
  call. Used as the fallback so the template runs with zero setup.

## Run

```bash
voodoo dev          # -> http://localhost:8000
```

Open http://localhost:8000 and click **Run**. The agent calls `get_time`, then
composes a final answer from the tool result — and its activity streams into
the browser log in realtime over the WebSocket transport.

## Use a real model (DeepSeek via `.env`)

The live provider reads its credentials from environment variables loaded from
`.env`:

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://litellm-database-production-6802.up.railway.app/v1
DEEPSEEK_MODEL=deepseek-v4-flash
```

| Variable            | Purpose                                                        |
| ------------------- | -------------------------------------------------------------- |
| `DEEPSEEK_API_KEY`  | API key for the endpoint. When unset, the demo provider is used. |
| `DEEPSEEK_BASE_URL` | Any OpenAI-compatible base URL (defaults to the OpenAI API).    |
| `DEEPSEEK_MODEL`    | Model id passed to the endpoint.                                |

Because the provider talks plain OpenAI chat-completions, you can point
`DEEPSEEK_BASE_URL` at any compatible gateway — DeepSeek, OpenRouter, Ollama,
vLLM, etc. — with no code changes.

> **Dependencies**: the provider uses the `openai` SDK and `python-dotenv`,
> both of which ship as dependencies of `voodoo-framework`, so a normal
> `voodoo new` / `.venv` install already has them.

## How it works

- `app/ai/tools.py` registers `get_time`, `roll_dice`, and `count_words` with
  `@tool` in the shared `ToolRegistry`. The agent gets them by name via
  `tools=[...]`.
- `app/ai/providers/` defines one module per provider:
  - `demo.py` — `DemoProvider`, fully offline; first returns `[TOOL: get_time]`,
    then answers from the tool result.
  - `deepseek.py` — `DeepSeekProvider`, a `LLMProvider` subclass that wraps
    `openai.AsyncOpenAI`, translates the agent's tool specs into OpenAI
    function-call form, and maps native tool calls back to the agent's
    `[TOOL: ...]` convention.
- `app/ai/agent.py` selects the model based on whether `DEEPSEEK_API_KEY` is
  set, builds the `Agent`, and handles mesh events (`agent.started`,
  `agent.tool.started`, `agent.completed`) with `@mesh.on(...)`, pushing them
  to the browser with `ws_manager.broadcast_append(...)`.
- `main.py` loads `.env`, imports `app.ai.providers` (which registers both
  providers via `register_provider(...)`, resolving as `demo:demo` and
  `deepseek:<model>`), then imports `app.ai.agent` (which pulls in
  `app.ai.tools`).
- `app/page.py` renders the chat UI and wires the input/button to the agent
  with `@event` handlers. The final answer is patched into the DOM with
  `ws_manager.broadcast_patch(...)` after `await agent.run(...)`.

## Swap in another framework provider

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
main.py              # entry point: env, providers, app boot
app/                 # application package (folder-based routing)
  page.py            # the chat page (folder-based routing -> /)
  ai/                # the AI layer
    agent.py         # Agent + model selection + realtime mesh handlers
    tools.py         # the @tool functions the agent can call
    providers/       # one module per model provider
      demo.py        # offline demo provider
      deepseek.py    # live OpenAI-compatible provider
.env.example         # template for the DeepSeek credentials
voodoo.toml          # app config
.voodoo/theme/       # theme snapshot + bespoke styles
```
