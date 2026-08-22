"""Chat page — a ChatGPT/Claude-style assistant with chat history.

Layout (all server-rendered, realtime updates over the WebSocket transport):

    ┌ sidebar ────────────────┬ chat-main ──────────────────────┐
    │ brand + New chat        │ header (menu toggle · model)    │
    │ chat history list       │ scrollable #chat-scroll         │
    │ (open / delete)         │   #chat-content (patched)       │
    │ model footer            │   └ #chat-messages / empty state│
    │                         │ composer (input + send)         │
    └─────────────────────────┴─────────────────────────────────┘

* clicking a chat (or New chat) patches ``#chat-content`` + ``#chat-list``,
  and the client syncs ``?chat=<id>`` into the URL (no reload);
* sending a message auto-creates a chat if none is open, appends the user
  bubble + a "thinking" bubble (spinner + live tool feed), then patches the
  thinking bubble into the final answer + meta line;
* every message is persisted via :mod:`app.chat_store` (SQLite), so reloading
  restores the conversation;
* a tiny inline script adds Enter-to-send, sidebar toggle (collapsed on
  desktop / overlay on mobile), auto-scroll, and URL sync.

Multi-turn agent history is intentionally single-shot per message: each
``run`` sends only the new prompt, and the full transcript lives in the UI
(the chat store) rather than being replayed into the model.
"""

import itertools
import re
from html import escape as _html_escape

from voodoo import Badge, Button, Div, Heading, Input, Text, event, ws_manager
from voodoo.seo import SEO
from voodoo.ui import Html

from app.ai.agent import MODEL_LABEL, MODEL_SUB, agent
from app.chat_store import (
    add_message,
    create_chat,
    delete_chat as store_delete_chat,
    get_chat,
    get_messages,
    list_chats,
)

__all__ = ["page"]

# Monotonic id source for the per-turn "thinking" bubble (patched on completion).
_turn_ids = itertools.count(1)

_SUGGESTIONS = (
    "What time is it?",
    "Roll a d20",
    "Count the words in hello world",
)

_SPINNER_HTML = (
    '<span class="spinner" role="status" aria-label="Thinking">'
    '<span class="spinner-dot"></span>'
    '<span class="spinner-dot"></span>'
    '<span class="spinner-dot"></span>'
    "</span>"
)


def _js_str(text: str) -> str:
    """Escape a string for use inside a single-quoted JS string literal."""
    return text.replace("\\", "\\\\").replace("'", "\\'")


# ───────────────────────────────────────────────────────────────────────
# Markdown → safe HTML (code, bold, italic, newlines)
# ───────────────────────────────────────────────────────────────────────

def _render_markdown(text: str) -> str:
    """Turn a small markdown subset into HTML, escaping everything first."""
    out = _html_escape(str(text))
    out = re.sub(
        r"```([\w+-]*)\n(.*?)```",
        lambda m: f'<pre class="code-block"><code>{m.group(2)}</code></pre>',
        out,
        flags=re.S,
    )
    out = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


# ───────────────────────────────────────────────────────────────────────
# Message bubbles (rendered to HTML so the server can patch/append them)
# ───────────────────────────────────────────────────────────────────────

def _user_bubble(text: str) -> str:
    # `.msg-row--user` uses `row-reverse`, so avatar-first lands on the right.
    return Div(
        Div("You", class_="avatar avatar--user"),
        Div(Html(_render_markdown(text)), class_="bubble bubble--user"),
        class_="msg-row msg-row--user",
    ).render()


def _assistant_bubble(text: str, meta: str = "", error: bool = False) -> str:
    cls = "bubble bubble--assistant" + (" bubble--error" if error else "")
    children: list = [Html(_render_markdown(text))]
    if meta:
        children.append(Text(meta, class_="msg-meta"))
    return Div(
        Div("AI", class_="avatar avatar--assistant"),
        Div(
            Div(*children, class_=cls),
            class_="msg-body",
        ),
        class_="msg-row msg-row--assistant",
    ).render()


def _thinking_bubble(think_id: str) -> str:
    return Div(
        Div("AI", class_="avatar avatar--assistant"),
        Div(
            Div(
                Html(_SPINNER_HTML),
                Div(id="agent-log", class_="agent-log"),
                class_="bubble bubble--assistant bubble--thinking",
            ),
            class_="msg-body",
        ),
        id=think_id,
        class_="msg-row msg-row--assistant",
    ).render()


def _messages_html(chat_id: str) -> str:
    """Rendered history for a chat (used on load / chat switch)."""
    parts = []
    for msg in get_messages(chat_id):
        if msg["role"] == "user":
            parts.append(_user_bubble(msg["content"]))
        else:
            parts.append(_assistant_bubble(msg["content"], meta=msg["meta"] or ""))
    return "".join(parts)


# ───────────────────────────────────────────────────────────────────────
# Sidebar + main content fragments (patch targets)
# ───────────────────────────────────────────────────────────────────────

def _chat_list_html(active_id: str | None = None) -> str:
    """``#chat-list`` — the sidebar history, active chat highlighted."""
    items = []
    for chat in list_chats():
        cid = chat["id"]
        active = " is-active" if cid == active_id else ""
        title = _html_escape(chat["title"] or "New chat")
        items.append(
            f'<div class="chat-item{active}" data-id="{cid}" '
            f'onclick="openChat(\'{cid}\')">'
            f'<span class="chat-item-ico">💬</span>'
            f'<span class="chat-item-title">{title}</span>'
            f'<button class="chat-item-del" title="Delete chat" '
            f'onclick="event.stopPropagation(); deleteChat(\'{cid}\')">🗑</button>'
            f"</div>"
        )
    if not items:
        body = (
            '<div class="chat-list-empty">No chats yet.<br>'
            "Ask something below to start one.</div>"
        )
    else:
        body = "".join(items)
    return f'<div id="chat-list" class="chat-list">{body}</div>'


def _chips_html() -> str:
    return "".join(
        f'<div class="chip" onclick="askPreset(\'{_js_str(label)}\')">'
        f"{_html_escape(label)}</div>"
        for label in _SUGGESTIONS
    )


def _empty_state_html() -> str:
    return (
        '<div id="chat-content" data-chat-id="">'
        '<div class="chat-empty">'
        '<div class="empty-emoji">✦</div>'
        '<h2 class="empty-title">How can I help?</h2>'
        '<p class="empty-sub">Ask for the time, roll some dice, or count words. '
        "The assistant calls tools and streams its trace live.</p>"
        f'<div class="chips">{_chips_html()}</div>'
        "</div>"
        "</div>"
    )


def _content_html(chat_id: str | None, empty: bool = False) -> str:
    """``#chat-content`` — the patched main area.

    ``empty=True`` renders a fresh, message-less ``#chat-messages`` container
    (used right after creating a chat so appends have a target).
    """
    if chat_id is None or get_chat(chat_id) is None:
        return _empty_state_html()
    msgs = "" if empty else _messages_html(chat_id)
    return (
        f'<div id="chat-content" data-chat-id="{chat_id}">'
        f'<div id="chat-messages" class="chat-messages">{msgs}</div>'
        "</div>"
    )


# ───────────────────────────────────────────────────────────────────────
# Client-side glue (sidebar, Enter-to-send, URL sync, auto-scroll)
# ───────────────────────────────────────────────────────────────────────

_CLIENT_SCRIPT = """
<script>
(function () {
    var currentChatId =
        new URLSearchParams(window.location.search).get('chat') || null;

    function scrollEl() { return document.getElementById('chat-scroll'); }

    function nearBottom() {
        var el = scrollEl();
        if (!el) return true;
        return el.scrollHeight - el.scrollTop - el.clientHeight < 140;
    }

    function scrollToBottom(force) {
        var el = scrollEl();
        if (el && (force || nearBottom())) el.scrollTop = el.scrollHeight;
    }

    function syncFromDom() {
        var el = document.getElementById('chat-content');
        if (!el) return;
        var id = el.getAttribute('data-chat-id');
        if (id !== currentChatId) {
            currentChatId = id;
            if (id) history.pushState(null, '', '/?chat=' + encodeURIComponent(id));
            else history.pushState(null, '', '/');
        }
    }

    window.toggleSidebar = function () {
        var shell = document.getElementById('app-shell');
        if (!shell) return;
        if (window.innerWidth <= 768) {
            shell.classList.toggle('sidebar-open');
        } else {
            shell.classList.toggle('sidebar-collapsed');
            try {
                localStorage.setItem('voodoo.sidebar',
                    shell.classList.contains('sidebar-collapsed') ? 'collapsed' : 'open');
            } catch (e) {}
        }
    };

    window.closeSidebar = function () {
        var shell = document.getElementById('app-shell');
        if (shell) shell.classList.remove('sidebar-open');
    };

    window.newChat = function () {
        window.voodoo.sendEvent('new_chat', 'new-chat-btn', '');
        setTimeout(syncFromDom, 120);
    };

    window.openChat = function (id) {
        window.voodoo.sendEvent('open_chat', 'chat-item-' + id, id);
        setTimeout(syncFromDom, 120);
    };

    window.deleteChat = function (id) {
        window.voodoo.sendEvent('delete_chat', 'chat-item-' + id,
            { id: id, active: currentChatId });
        if (id === currentChatId) {
            // Server deletes it; reload home to land on the empty state.
            setTimeout(function () { window.location.href = '/'; }, 150);
        }
    };

    window.askPreset = function (text) {
        var input = document.getElementById('prompt-input');
        if (input) input.value = text;
        window.voodooSend();
    };

    window.voodooSend = function () {
        var input = document.getElementById('prompt-input');
        if (!input) return;
        var text = (input.value || '').trim();
        if (!text) return;
        window.voodoo.sendEvent('run_agent', input.id,
            { chat: currentChatId, text: text });
        input.value = '';
        input.focus();
    };

    function setup() {
        var shell = document.getElementById('app-shell');
        if (shell) {
            try {
                if (localStorage.getItem('voodoo.sidebar') === 'collapsed') {
                    shell.classList.add('sidebar-collapsed');
                }
            } catch (e) {}
        }

        var scroller = document.getElementById('chat-scroll');
        if (scroller) {
            scrollToBottom(true);
            new MutationObserver(function (mutations) {
                var replaced = false;
                for (var i = 0; i < mutations.length; i++) {
                    var added = mutations[i].addedNodes;
                    for (var j = 0; j < added.length; j++) {
                        var n = added[j];
                        if (n.nodeType === 1 &&
                            (n.id === 'chat-content' || n.id === 'chat-messages')) {
                            replaced = true;
                        }
                    }
                }
                if (replaced) { scrollToBottom(true); syncFromDom(); }
                else scrollToBottom(false);
            }).observe(scroller, { childList: true, subtree: true });
        }

        document.addEventListener('keydown', function (e) {
            var input = document.getElementById('prompt-input');
            if (e.key === 'Enter' && !e.shiftKey &&
                input && document.activeElement === input) {
                e.preventDefault();
                window.voodooSend();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setup);
    } else {
        setup();
    }
})();
</script>
"""


# ───────────────────────────────────────────────────────────────────────
# Page
# ───────────────────────────────────────────────────────────────────────

def page(request):
    chat_id = request.query_params.get("chat")
    if chat_id and get_chat(chat_id) is None:
        chat_id = None

    seo = SEO(
        title="Voodoo AI Assistant",
        description="A realtime AI chat with tool calling and chat history, "
        "built on Voodoo.",
    )

    ui = Div(
        # ── Sidebar ───────────────────────────────────────────────────
        Div(
            Html(
                '<div class="sidebar-brand">'
                '<img class="brand-logo" src="/public/voodoo-logo-white.png" '
                'alt="Voodoo AI" />'
                "</div>"
            ),
            Button("＋ New chat", onclick="newChat()", class_="new-chat"),
            Html(_chat_list_html(chat_id)),
            Html(f'<div class="sidebar-foot">⚡ {_html_escape(MODEL_LABEL)}</div>'),
            class_="sidebar",
            id="sidebar",
        ),
        # ── Main column ───────────────────────────────────────────────
        Div(
            Div(
                Button("☰", onclick="toggleSidebar()", class_="menu-btn",
                       title="Toggle sidebar"),
                Div(
                    Heading("AI Assistant", level=1, class_="chat-title"),
                    Text("Realtime chat with tool calling", class_="chat-sub"),
                    class_="chat-header-text",
                ),
                Div(
                    Badge(MODEL_LABEL),
                    Text(MODEL_SUB, class_="muted"),
                    class_="chat-header-model",
                ),
                class_="chat-header",
            ),
            Div(
                Html(_content_html(chat_id)),
                id="chat-scroll",
                class_="chat-scroll",
            ),
            Div(
                Div(
                    Input(
                        id="prompt-input",
                        placeholder="Message the assistant…",
                        class_="composer-input",
                    ),
                    Button("➤", onclick="voodooSend()", class_="composer-send",
                           title="Send"),
                    class_="composer",
                ),
                Html('<div class="composer-hint">AI Assistant can make mistakes.</div>'),
                class_="composer-wrap",
            ),
            class_="chat-main",
        ),
        Html('<div class="sidebar-backdrop" onclick="closeSidebar()"></div>'),
        Html(_CLIENT_SCRIPT),
        class_="app-shell",
        id="app-shell",
    )

    return seo, ui


# ───────────────────────────────────────────────────────────────────────
# Events (WebSocket)
# ───────────────────────────────────────────────────────────────────────

@event
async def new_chat(element_id, value):
    """Create an empty chat and show it."""
    chat_id = create_chat()
    await ws_manager.broadcast_patch("chat-content", _content_html(chat_id, empty=True))
    await ws_manager.broadcast_patch("chat-list", _chat_list_html(chat_id))


@event
async def open_chat(element_id, value):
    """Load an existing chat's history into the main area."""
    if not value or get_chat(value) is None:
        return
    await ws_manager.broadcast_patch("chat-content", _content_html(value))
    await ws_manager.broadcast_patch("chat-list", _chat_list_html(value))


@event
async def delete_chat(element_id, value):
    """Remove a chat (messages cascade). If it was the active chat, reset the
    main area to the empty state too (deleting client reloads to ``/``)."""
    if isinstance(value, dict):
        chat_id, active = value.get("id"), value.get("active")
    else:
        chat_id, active = value, None
    if not chat_id:
        return
    store_delete_chat(chat_id)
    await ws_manager.broadcast_patch("chat-list", _chat_list_html(active))
    if chat_id == active:
        await ws_manager.broadcast_patch("chat-content", _empty_state_html())


@event
async def run_agent(element_id, value):
    """Send a message: append bubbles, run the agent, persist the exchange."""
    payload = value if isinstance(value, dict) else {}
    text = (payload.get("text") or "").strip()
    if not text:
        return
    chat_id = payload.get("chat") or None

    # Auto-create a chat when none is open (ChatGPT-style), so the new
    # conversation shows up in the sidebar with a fresh #chat-messages target.
    if chat_id is None or get_chat(chat_id) is None:
        chat_id = create_chat()
        await ws_manager.broadcast_patch(
            "chat-content", _content_html(chat_id, empty=True)
        )
        await ws_manager.broadcast_patch("chat-list", _chat_list_html(chat_id))

    add_message(chat_id, "user", text)

    think_id = f"think-{next(_turn_ids)}"
    await ws_manager.broadcast_append("chat-messages", _user_bubble(text))
    await ws_manager.broadcast_append("chat-messages", _thinking_bubble(think_id))

    run = await agent.run(text)

    if run.error or run.status != "completed":
        content = run.error or run.output or "Something went wrong."
        answer = _assistant_bubble(content, error=True)
        meta = ""
    else:
        meta = (
            f"{run.provider} · {run.tokens_out} tokens · "
            f"{len(run.tool_calls)} tool call(s) · "
            f"{run.timings['total_ms']:.0f} ms"
        )
        answer = _assistant_bubble(run.output, meta=meta)
        content = run.output

    add_message(chat_id, "assistant", content, meta=meta)

    # Swap the thinking bubble for the final answer (or error).
    await ws_manager.broadcast_patch(think_id, answer)

    # The chat may have been titled/ordered by the new messages — refresh list.
    await ws_manager.broadcast_patch("chat-list", _chat_list_html(chat_id))
