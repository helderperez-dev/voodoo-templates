"""Model providers for the agent.

Each provider lives in its own module. Registering a new one is a single
``register_provider(...)`` line below — the name becomes the ``provider:``
prefix in ``Agent(model="<name>:<model>")``.
"""

from voodoo.ai.providers import register_provider

register_provider("demo", "app.ai.providers.demo.DemoProvider")
register_provider("deepseek", "app.ai.providers.deepseek.DeepSeekProvider")

__all__ = ["register_provider"]
