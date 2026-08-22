"""Chat page — ``/chat/{chat_id}`` renders a specific conversation.

The folder ``[chat_id]`` maps to a ``{chat_id}`` path parameter (folder-based
routing). The shared implementation lives in :mod:`app.chat_ui`; the root
``/`` route lives in ``app/page.py``.
"""

from app.chat_ui import render_page

__all__ = ["page"]


def page(request, chat_id: str | None = None):
    """Render the chat shell for the given conversation.

    An unknown/deleted id renders the empty state; the client script then
    syncs the URL back to ``/`` (see ``syncFromDom``).
    """
    return render_page(chat_id)
