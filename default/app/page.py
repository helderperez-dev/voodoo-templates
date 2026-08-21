"""Voodoo starter — a single route. Add more by dropping a page.py in a folder."""

from voodoo import (
    A,
    Brand,
    Flex,
    Heading,
    Img,
    Stack,
    Text,
    ThemeToggle,
)
from voodoo.seo import OpenGraph, SEO
from voodoo.ui.component import Html

_GH_URL = "https://github.com/helderperez-dev/voodoo"
_DOCS_URL = "https://github.com/helderperez-dev/voodoo#readme"


def _logo() -> Brand:
    """One black wordmark; custom.css inverts it to white in dark mode."""
    return Brand(
        Img(src="/public/voodoo-logo-black.png", alt="Voodoo", class_="brand-logo"),
        href="/",
    )


def page(request):
    seo = SEO(
        title="Voodoo App",
        description="One runtime for adaptive software.",
        og=OpenGraph(
            title="Voodoo App",
            description="One runtime for adaptive software.",
            type="website",
            site_name="Voodoo",
        ),
    )

    hero = Stack(
        _logo(),
        Heading(
            "One runtime for ",
            Html('<span class="accent">adaptive</span>'),
            " software.",
            level=1,
            class_="hero-title",
        ),
        Text(
            "Web, APIs, agents, and events — first-class in Python.",
            class_="hero-sub",
        ),
        Flex(
            A("GitHub", href=_GH_URL, target="_blank", class_="hero-link hero-link--solid"),
            A("Docs", href=_DOCS_URL, target="_blank", class_="hero-link"),
            direction="row",
            items="center",
            justify="center",
            gap="md",
            wrap="wrap",
        ),
        gap="lg",
        items="center",
        class_="hero",
    )

    ui = Flex(
        hero,
        ThemeToggle(class_="theme-fab"),
        justify="center",
        items="center",
        class_="shell",
    )

    return seo, ui
