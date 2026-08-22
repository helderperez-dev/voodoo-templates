# Voodoo AI Agent

A ChatGPT/Claude-style AI chat with tool calling, a realtime trace, and chat
history — all rendered from Python, no hand-written JavaScript.

It ships with one live provider, **`deepseek:<model>`** — a real model served
through an OpenAI-compatible (LiteLLM) endpoint, configured via `.env`.

## Run

```bash
voodoo dev          # -> http://localhost:8000
```

Open http://localhost:8000 and start chatting. The agent calls tools like
`get_time`, then composes a final answer from the tool result — and its
activity streams into a "thinking" bubble (spinner + live log) over the
WebSocket transport.

## Chat history sidebar

- **New chat** — start a fresh conversation; the first message becomes its
  title.
- **History list** — click any chat to reopen it; messages are persisted
  locally in `.data/chat.db` (SQLite).
- **Delete** — hover a chat and hit 🗑; deleting the open chat returns you to
  the landing state.
- **Collapse** — the ☰ button hides the sidebar on desktop (state is
  remembered) and turns it into an off-canvas overlay on mobile.

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
| `DEEPSEEK_API_KEY`  | API key for the endpoint. |
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
  - `deepseek.py` — `DeepSeekProvider`, a `LLMProvider` subclass that wraps
    `openai.AsyncOpenAI`, translates the agent's tool specs into OpenAI
    function-call form, and maps native tool calls back to the agent's
    `[TOOL: ...]` convention.
- `app/ai/agent.py` builds the `Agent` on the live `deepseek:<model>` provider,
  and handles mesh events (`agent.started`,
  `agent.tool.started`, `agent.completed`) with `@mesh.on(...)`, pushing them
  to the browser with `ws_manager.broadcast_append(...)`.
- `main.py` loads `.env`, imports `app.ai.providers` (which registers the
  `deepseek` provider via `register_provider(...)`), then imports
  `app.ai.agent` (which pulls in `app.ai.tools`).
- `app/page.py` renders the chat UI and wires the input/button to the agent
  with `@event` handlers. The final answer is patched into the DOM with
  `ws_manager.broadcast_patch(...)` after `await agent.run(...)`.
- `app/chat_store.py` persists chats and messages to a local SQLite database
  (`.data/chat.db`, WAL mode) with a fresh connection per call.

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

Supported providers include `openai:*`, `anthropic:*`, and `mock:*`. See the
framework docs for the full list and env-var names.

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
      deepseek.py    # live OpenAI-compatible provider
.env.example         # template for the DeepSeek credentials
voodoo.toml          # app config
.voodoo/theme/       # theme snapshot + bespoke styles
```
