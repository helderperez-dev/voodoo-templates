"""The application package.

Folder-based routing imports every ``page.py`` it finds (``app/page.py`` →
``/``). Everything else — the ``app/ai/`` layer (agent, tools, providers) — is
ordinary Python imported explicitly from ``main.py`` and ``app/page.py``.
"""
