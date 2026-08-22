"""The AI layer — the agent, its tools, and its model providers.

``main.py`` imports :mod:`app.ai.providers` (registering the providers) and
:mod:`app.ai.agent` (building the ``Agent`` + realtime mesh handlers, which
pulls in :mod:`app.ai.tools` for its ``@tool`` registrations).
"""
