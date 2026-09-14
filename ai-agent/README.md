# Voodoo AI Agent

A ChatGPT-style AI chat with tool calling and persistent history — one
Python file (`main.py`, ~285 lines), **zero hand-written CSS, zero inline
JavaScript, zero custom provider classes**. Everything is a Voodoo framework
primitive.

The live model (DeepSeek, or any OpenAI-compatible endpoint) is configured
entirely in `voodoo.toml` + `.env` — the `[ai]` block. No provider code.

## Run

```bash
voodoo dev          # -> http://localhost:8000
```

Open http://localhost:8000 and start chatting. The agent calls tools like
`get_time`, then composes the final answer (native tool calling — no text
markers). Every conversation has a clean URL — `/chat/<id>` — bookmarkable
and restorable on reload. Messages persist in Voodoo's Store-first runtime at
`.voodoo/application.vstore`.

## Use a real model (DeepSeek via `.env`)

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1   # or any OpenAI-compatible gateway
```

The model itself is declared in `voodoo.toml`:

```toml
[ai]
provider = "openai"                                # OpenAI-compatible client
model = "deepseek-chat"                            # any model id
base_url = "${DEEPSEEK_BASE_URL:https://api.deepseek.com/v1}"
api_key = "${DEEPSEEK_API_KEY}"
```

Because the framework talks plain OpenAI chat-completions, you can point
`base_url` at any compatible gateway — DeepSeek, OpenRouter, Ollama, vLLM —
with no code changes.

## How it works

- **`[ai]` config → Agent** — `Agent()` (no arguments!) resolves its model,
  base URL, and API key from the `[ai]` block. That's the whole provider
  setup.
- **`app/ai/tools.py`** registers `get_time`, `roll_dice`, `count_words`
  with `@tool`; the agent gets them by name via `tools=[...]`.
- **Native tool calling** — the framework's `ToolCall` protocol carries
  structured tool requests (and streams their deltas); the agent executes,
  appends the result, and loops to the final answer.
- **ORM queries** — chats/messages are `Model` subclasses; history uses
  `Model.where(...).order_by(...)` and a `FK[Chat]` cascade delete. No raw
  SQL anywhere.
- **Store-first durability** — model state is stored in
  `.voodoo/application.vstore` by default. SQLite/PostgreSQL are explicit
  adapters rather than hidden defaults.
- **Chat UI primitives** — `Sidebar`, `MessageList`, `ChatMessage`,
  `Composer`, `Icon`, `Markdown`, `StreamingText` are server components
  styled by the theme system. Enter-to-send, auto-grow, and auto-scroll ship
  in the framework's client SDK.
- **Realtime** — `@event` handlers run on WebSocket messages and patch the
  DOM with `ws_manager.broadcast_patch(...)`; no page reloads.
- **Multi-turn** — each send replays the stored transcript into
  `agent.run(text, history=[...])`, so the model sees the full conversation.

## Swap the model

Change the `[ai]` block in `voodoo.toml` — e.g. `model = "gpt-4o"` with
`base_url = ""` for OpenAI proper — or use a routing alias
(`model = "best"`). Nothing else changes; see the framework docs.

## Project layout

```
main.py                    # the whole app: models, pages, events, agent
app/ai/tools.py            # the @tool functions the agent can call
voodoo.toml                # [ai] provider config (model, base_url, api key)
.env.example               # template for endpoint credentials
.voodoo/application.vstore # local durable application infrastructure
.voodoo/theme/             # theme snapshot (swap with `voodoo theme use ...`)
```
