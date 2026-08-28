"""AI Agent — a ChatGPT-style assistant in one file, on the Voodoo runtime.

Agent from ``[ai]`` in voodoo.toml (zero provider code) · ``@tool`` functions ·
``Model`` queries + ``FK`` cascades (zero SQL) · ``MessageList``/``ChatMessage``/
``Composer``/``Sidebar``/``Icon``/``Markdown`` components (zero CSS/JS — the
client SDK provides Enter-to-send + auto-scroll) · ``@event`` WebSocket handlers.

Run: ``voodoo dev`` (or ``python main.py``) → http://localhost:8000
"""

from __future__ import annotations

import time
from typing import Any

from voodoo import (
    App,
    Agent,
    Button,
    ChatMessage,
    Composer,
    Div,
    Flex,
    Heading,
    Html,
    Icon,
    Markdown,
    MessageList,
    Sidebar,
    Stack,
    Text,
    event,
    page,
    ws_manager,
)
from voodoo.data import FK, Model
from voodoo.seo import SEO

import app.ai.tools  # noqa: F401 — imported for its @tool registrations

# --- Models (FK cascade: deleting a Chat removes its Messages) ---------------------------------------------------------------


class Chat(Model):
    __tablename__ = "chats"
    title: str
    created_at: int
    updated_at: int


class Message(Model):
    __tablename__ = "messages"
    chat_id: FK[Chat]
    role: str
    content: str
    meta: str = ""
    created_at: int


agent = Agent(  # model resolved from [ai] in voodoo.toml
    tools=["get_time", "roll_dice", "count_words"],
    system_prompt=(
        "You are a helpful assistant. Use the available tools when the user "
        "asks for the current time, a random number or dice roll, or a word "
        "count. Otherwise answer directly."
    ),
)

SUGGESTIONS = (
    "What time is it?",
    "Roll a d20",
    'Count the words in: "to be or not to be"',
)

# --- Fragments (server-rendered; patched over WebSocket) ---------------------------------------------------------------


async def chat_list_html(active_id: Any = None) -> str:
    chats = await Chat.where().order_by("-updated_at").limit(50)
    if not chats:
        return Div(Text("No conversations yet", tone="muted"), id="chat-list").render()
    rows = [
        Flex(
            Button(c.title or "New chat", on_click="open_chat", value=str(c.id)),
            Button(
                Icon("trash", label="Delete"),
                on_click="delete_chat",
                value=f'{{"id": "{c.id}", "active": "{active_id or ""}"}}',
            ),
            justify="between",
            class_="vd-chat-row",
        )
        for c in chats
    ]
    return Div(*rows, id="chat-list").render()


async def messages_html(chat_id: int) -> str:
    msgs = await Message.where(chat_id=chat_id).order_by("id")
    return MessageList(
        *[
            ChatMessage(
                Markdown(m.content) if m.role == "assistant" else m.content,
                role=m.role,
            )
            for m in msgs
        ],
        id="chat-messages",
    ).render()


async def chat_area_html(chat_id: int | None) -> str:
    """Main area: the transcript + composer, or the empty state."""
    composer = Composer(on_send="send", placeholder="Ask anything…")
    if chat_id is None or await Chat.get(chat_id) is None:
        return Stack(
            Heading("What can I help with?", level=2),
            Div(
                *[Button(s, on_click="send_suggestion", value=s) for s in SUGGESTIONS],
                class_="vd-suggestions",
            ),
            composer,
            id="chat-main",
            gap="lg",
        ).render()
    return Stack(
        Div(
            await messages_html(chat_id),
            class_="vd-chat-scroll",
            **{"data-vd-auto-scroll": "bottom"},
        ),
        composer,
        id="chat-main",
        gap="md",
    ).render()


def shell_html(main_html: str, list_html: str) -> str:
    """The app frame: sidebar (history) + main area.

    Fragments arrive pre-rendered; ``Html`` embeds them without escaping.
    """
    return Flex(
        Sidebar(
            Stack(
                Button("＋ New chat", on_click="new_chat"),
                Div(Html(list_html), id="chat-list"),
                gap="sm",
            ),
        ),
        Div(Html(main_html), class_="vd-chat-main"),
        class_="vd-app-shell",
    ).render()


# --- Pages ---------------------------------------------------------------


@page("/")
async def home(request):
    return (
        SEO(title="AI Agent", description="A Voodoo-powered assistant"),
        shell_html(await chat_area_html(None), await chat_list_html(None)),
    )


@page("/chat/{chat_id}")
async def chat_page(request, chat_id: str):
    try:
        cid = int(chat_id)
    except (TypeError, ValueError):
        cid = None
    return (
        SEO(title="AI Agent — Chat"),
        shell_html(await chat_area_html(cid), await chat_list_html(cid)),
    )


# --- Events (WebSocket → handler → DOM patch; no client JS written by us) ---------------------------------------------------------------


async def _patch(cid: int | None, main: bool = True, listing: bool = True) -> None:
    """Broadcast DOM patches for the main area and/or the sidebar list."""
    if listing:
        await ws_manager.broadcast_patch("chat-list", await chat_list_html(cid))
    if main:
        await ws_manager.broadcast_patch("chat-main", await chat_area_html(cid))


@event
async def new_chat(element_id, value):
    now = int(time.time())
    chat = await Chat.create(title="New chat", created_at=now, updated_at=now)
    await _patch(chat.id)


@event
async def open_chat(element_id, value):
    try:
        cid = int(value)
    except (TypeError, ValueError):
        return
    if await Chat.get(cid) is not None:
        await _patch(cid)


@event
async def delete_chat(element_id, value):
    """FK cascade removes the chat's messages too."""
    import json as _json

    payload = value
    if isinstance(value, str):  # buttons pass their value= attribute verbatim
        try:
            payload = _json.loads(value)
        except _json.JSONDecodeError:
            payload = {"id": value}
    chat_id = (payload or {}).get("id")
    if not chat_id:
        return
    chat = await Chat.get(int(chat_id))
    if chat:
        await chat.delete()
    active = (payload or {}).get("active") or None
    await _patch(active, main=str(chat_id) == str(active))


@event
async def send(element_id, value):
    """Append the user turn, run the agent (with history), patch the answer."""
    text = (value or "").strip() if isinstance(value, str) else str(value or "").strip()
    if not text:
        return

    # Reuse the most recently active chat; create one if none exists.
    latest = await Chat.where().order_by("-updated_at").limit(1)
    if latest:
        chat, cid = latest[0], latest[0].id
    else:
        now = int(time.time())
        chat = await Chat.create(title=text[:48], created_at=now, updated_at=now)
        cid = chat.id

    # Multi-turn: replay prior transcript into the agent.
    history = [
        {"role": m.role, "content": m.content}
        for m in await Message.where(chat_id=cid).order_by("id")
    ]

    await Message.create(
        chat_id=cid, role="user", content=text, created_at=int(time.time())
    )
    if chat.title == "New chat":
        chat.title = text[:48]
    chat.updated_at = int(time.time())
    await chat.save()
    await _patch(cid)

    run = await agent.run(text, history=history)

    if run.error or run.status != "completed":
        answer, meta = run.error or "Something went wrong.", ""
    else:
        n = len(run.tool_calls)
        meta = (
            f"{run.tokens_out} tokens · {n} tool call{'s' if n != 1 else ''} "
            f"· {run.timings['total_ms']:.0f} ms"
        )
        answer = run.output

    await Message.create(
        chat_id=cid, role="assistant", content=answer, meta=meta,
        created_at=int(time.time()),
    )
    await _patch(cid)


@event
async def send_suggestion(element_id, value):
    """Suggestion chips reuse the composer's send flow."""
    await send(element_id, value)


# --- App ---------------------------------------------------------------

app = App()

if __name__ == "__main__":
    app.run()
