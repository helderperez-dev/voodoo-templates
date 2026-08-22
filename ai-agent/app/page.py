"""Chat page — a ChatGPT/Claude-style assistant UI at ``/``.

Rendered entirely from Python via the Voodoo component library. Realtime
updates flow over the WebSocket transport:

* user / assistant bubbles are appended to ``#chat-messages``;
* a "thinking" bubble (spinner + live tool-activity feed) is appended while
  the agent runs, then patched into the final answer + meta line.

A small inline script adds the three things the framework doesn't model yet:
Enter-to-send, input clearing + refocus, and auto-scroll.
"""

import itertools
import re
from html import escape as _html_escape

from voodoo import Badge, Button, Div, Heading, Input, Text, event, ws_manager
from voodoo.seo import SEO
from voodoo.ui import Html

from app.ai.agent import MODEL_LABEL, MODEL_SUB, agent

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
        Div(*children, class_="msg-body"),
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


def _suggestion_chips() -> list[Div]:
    return [
        Div(
            Text(label, class_="chip-label"),
            onclick=f"askPreset('{label}')",
            class_="chip",
        )
        for label in _SUGGESTIONS
    ]


# ───────────────────────────────────────────────────────────────────────
# Client-side glue (Enter-to-send, clear/refocus, auto-scroll)
# ───────────────────────────────────────────────────────────────────────

_CLIENT_SCRIPT = """
<script>
(function () {
    window.askPreset = function (text) {
        window.voodoo.sendEvent('run_agent', 'prompt-input', text);
    };

    window.voodooSend = function () {
        var input = document.getElementById('prompt-input');
        if (!input) return;
        var text = (input.value || '').trim();
        if (!text) return;
        window.voodoo.sendEvent('run_agent', input.id, text);
        input.value = '';
        input.focus();
    };

    function scrollToBottom() {
        var scroller = document.getElementById('chat-scroll');
        if (scroller) scroller.scrollTop = scroller.scrollHeight;
    }

    function setup() {
        var scroller = document.getElementById('chat-scroll');
        var messages = document.getElementById('chat-messages');
        if (scroller && messages) {
            scrollToBottom();
            new MutationObserver(scrollToBottom).observe(messages, {
                childList: true,
                subtree: true
            });
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


def page(request):
    seo = SEO(
        title="Voodoo AI Assistant",
        description="A realtime AI chat with tool calling, built on Voodoo.",
    )

    ui = Div(
        # Header — model identity
        Div(
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
        # Scrollable message area — empty state + appended messages
        Div(
            Div(
                Div("✦", class_="empty-emoji"),
                Heading("How can I help?", level=2, class_="empty-title"),
                Text(
                    "Ask for the time, roll some dice, or count words. "
                    "The assistant calls tools and streams its trace live.",
                    class_="empty-sub",
                ),
                Div(*_suggestion_chips(), class_="chips"),
                class_="chat-empty",
                id="chat-empty",
            ),
            Div(id="chat-messages", class_="chat-messages"),
            class_="chat-scroll",
        ),
        # Composer
        Div(
            Input(
                id="prompt-input",
                placeholder="Message the assistant…",
                class_="composer-input",
            ),
            Button("Send", onclick="voodooSend()", class_="composer-send"),
            class_="composer",
        ),
        Html(_CLIENT_SCRIPT),
        class_="chat-shell",
    )

    return seo, ui


@event
async def run_agent(element_id, value):
    prompt_text = (value or "").strip()
    if not prompt_text:
        return

    think_id = f"think-{next(_turn_ids)}"

    # Hide the empty-state prompt once a real conversation begins.
    await ws_manager.broadcast_patch("chat-empty", "")

    # Append the user's message, then a thinking bubble (spinner + tool feed).
    await ws_manager.broadcast_append("chat-messages", _user_bubble(prompt_text))
    await ws_manager.broadcast_append("chat-messages", _thinking_bubble(think_id))

    run = await agent.run(prompt_text)

    if run.error or run.status != "completed":
        html = _assistant_bubble(
            run.error or run.output or "Something went wrong.", error=True
        )
    else:
        meta = (
            f"{run.provider} · {run.tokens_out} tokens · "
            f"{len(run.tool_calls)} tool call(s) · "
            f"{run.timings['total_ms']:.0f} ms"
        )
        html = _assistant_bubble(run.output, meta=meta)

    # Swap the thinking bubble for the final answer (or error).
    await ws_manager.broadcast_patch(think_id, html)
