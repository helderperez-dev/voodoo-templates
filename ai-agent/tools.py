"""Agent tools — callable by the agent, over MCP, and as plain Python.

Each ``@tool`` registers into the shared ``ToolRegistry`` by name; the agent
references them via ``tools=["get_time", "roll_dice", "count_words"]``.
"""

from voodoo import tool


@tool
async def get_time() -> str:
    """Return the current time."""
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


@tool
async def roll_dice(sides: int = 6) -> int:
    """Roll a die with the given number of sides."""
    import random

    return random.randint(1, sides)


@tool
async def count_words(text: str) -> int:
    """Count the number of words in a string."""
    return len(text.split())
