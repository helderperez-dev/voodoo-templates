"""About route — app/about/page.py maps to /about.

Shows the folder-based routing story with a rendered file tree.
"""
from textwrap import dedent

from voodoo import (
    BackLink,
    Card,
    CodeBlock,
    Div,
    Eyebrow,
    Grid,
    Heading,
    Page,
    PageHero,
    Stack,
    Text,
)
from voodoo.ui.component import Html

from app._meta import page_seo, site_footer, site_nav

_TREE = dedent("""
    app/
    ├── page.py            →  /
    ├── about/
    │   └── page.py        →  /about
    └── users/
        └── [id]/
            └── page.py    →  /users/{id}
    """).strip()


def page(request):
    seo = page_seo(
        "About — Voodoo",
        "How folder-based routing works in Voodoo: the folder is the router.",
    )
    ui = Div(
        site_nav("about"),
        Page(
            Stack(
                PageHero(
                    Stack(
                        Eyebrow("app/about/page.py"),
                        Heading("The folder is the router", level=1),
                        Text(
                            "Folder-based routing maps directories to URLs — drop "
                            "a page.py in a folder and the route exists. No "
                            "registration, no config, no ceremony.",
                            tone="muted",
                        ),
                        gap="md",
                        items="start",
                    )
                ),
                Grid(
                    Card(
                        Stack(
                            Heading("One file per route", level=3),
                            Text(
                                "Each page.py exports a single page(request) "
                                "function that returns (SEO, UI). The framework "
                                "renders it server-side and wires up realtime.",
                                tone="muted",
                            ),
                            gap="md",
                        )
                    ),
                    Card(
                        Stack(
                            Heading("Dynamic segments", level=3),
                            Text(
                                "Bracket folders like [id] create dynamic routes, "
                                "and type annotations coerce the segment — try the "
                                "Users page.",
                                tone="muted",
                            ),
                            gap="md",
                        )
                    ),
                    cols="2",
                    gap="md",
                ),
                Stack(
                    CodeBlock(_TREE, language="text"),
                    BackLink("Back home"),
                    gap="md",
                    items="start",
                ),
                gap="xl",
            )
        ),
        site_footer(),
    )
    return seo, ui
