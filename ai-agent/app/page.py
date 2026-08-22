"""Root page — the chat shell with no conversation open (landing state).

The real implementation (shell, fragments, client script, WebSocket events)
lives in :mod:`app.chat_ui`; this file is just the ``/`` route. Per-chat
URLs are handled by ``app/chat/[chat_id]/page.py`` → ``/chat/{chat_id}``.
"""

from app.chat_ui import render_page

__all__ = ["page"]


def page(request):
    """Landing page: the app shell with the empty state."""
    return render_page(None)
