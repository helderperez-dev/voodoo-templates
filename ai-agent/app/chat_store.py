"""Chat history persistence — a small SQLite-backed store.

Stores conversations and their messages in ``.data/chat.db`` (git-ignored),
so history survives server restarts and dev-server reloads.

    chats      id, title, created_at, updated_at
    messages   id, chat_id, role (user|assistant), content, meta, created_at

The first user message of a chat becomes its sidebar title. Each helper opens
a fresh connection, which keeps the store safe to call from both the async
event loop (event handlers) and Starlette's sync threadpool (page rendering).
"""

from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path

__all__ = [
    "create_chat",
    "list_chats",
    "get_chat",
    "get_messages",
    "add_message",
    "delete_chat",
]

_DB_DIR = Path(__file__).resolve().parent.parent / ".data"
_DB_PATH = _DB_DIR / "chat.db"

_TITLE_MAX = 48  # sidebar title length cap


def _connect() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id         TEXT PRIMARY KEY,
                title      TEXT NOT NULL DEFAULT 'New chat',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         TEXT PRIMARY KEY,
                chat_id    TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                role       TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content    TEXT NOT NULL,
                meta       TEXT,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_chat
                ON messages(chat_id, created_at);
            """
        )


_init()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_chat() -> str:
    """Create an empty chat and return its id."""
    chat_id = uuid.uuid4().hex[:12]
    now = time.time()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (chat_id, "New chat", now, now),
        )
    return chat_id


def list_chats() -> list[dict]:
    """All chats, most recently active first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM chats ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_chat(chat_id: str) -> dict | None:
    """A single chat, or ``None`` if it doesn't exist."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, title, created_at, updated_at FROM chats WHERE id = ?",
            (chat_id,),
        ).fetchone()
    return dict(row) if row else None


def get_messages(chat_id: str) -> list[dict]:
    """All messages of a chat, oldest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, meta FROM messages "
            "WHERE chat_id = ? ORDER BY created_at ASC, rowid ASC",
            (chat_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_message(chat_id: str, role: str, content: str, meta: str = "") -> None:
    """Append a message and bump the chat to the top of the list.

    The first user message also becomes the chat's sidebar title.
    """
    now = time.time()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (id, chat_id, role, content, meta, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (uuid.uuid4().hex, chat_id, role, content, meta, now),
        )
        if role == "user":
            conn.execute(
                "UPDATE chats SET title = ?, updated_at = ? "
                "WHERE id = ? AND title = 'New chat'",
                (content.strip()[: _TITLE_MAX] or "New chat", now, chat_id),
            )
        else:
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id)
            )


def delete_chat(chat_id: str) -> None:
    """Delete a chat and all of its messages (FK cascade)."""
    with _connect() as conn:
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
