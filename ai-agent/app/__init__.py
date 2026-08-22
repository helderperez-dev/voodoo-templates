"""The application package.

Folder-based routing imports every ``page.py`` it finds (``app/page.py`` →
``/``). Everything else here — ``agent.py``, ``provider.py``, ``tools.py`` —
is ordinary Python imported explicitly from ``main.py`` and ``app/page.py``.
"""
