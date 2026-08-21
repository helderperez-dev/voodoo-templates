"""User route — app/users/[id]/page.py maps to /users/{id}.

Bracket folders create dynamic segments; the `id: int` annotation coerces
the path segment to the declared type.
"""
from voodoo import (
    A,
    BackLink,
    Card,
    Chip,
    Div,
    Eyebrow,
    Flex,
    Heading,
    Page,
    PageHero,
    Stack,
    Text,
)

from app._meta import page_seo, site_footer, site_nav


def page(request, id: int):
    seo = page_seo(
        f"User {id} — Voodoo",
        f"Dynamic route /users/{id}, powered by folder-based routing.",
    )
    ui = Div(
        site_nav("users"),
        Page(
            Stack(
                PageHero(
                    Stack(
                        Eyebrow("app/users/[id]/page.py"),
                        Flex(
                            Heading(f"User #{id}", level=1),
                            Chip("id: int → coerced"),
                            direction="row",
                            items="center",
                            gap="sm",
                            wrap="wrap",
                        ),
                        Text(
                            f"You're looking at /users/{id} — a dynamic segment "
                            "rendered by a single page.py.",
                            tone="muted",
                        ),
                        gap="md",
                        items="start",
                    )
                ),
                Card(
                    Stack(
                        Heading("How this route works", level=3),
                        Text(
                            "Bracket folders become dynamic segments: "
                            "app/users/[id]/page.py → /users/{id}. One file "
                            "handles every id.",
                            tone="muted",
                        ),
                        Text(
                            "The int annotation coerces the segment before your "
                            "function runs: '42' arrives as 42.",
                            tone="muted",
                        ),
                        gap="md",
                    )
                ),
                Stack(
                    Flex(
                        Text("Try another id:", class_="id-prompt"),
                        *[
                            A(str(i), href=f"/users/{i}", class_="id-chip")
                            for i in (1, 7, 42, 99)
                        ],
                        direction="row",
                        items="center",
                        gap="sm",
                        wrap="wrap",
                    ),
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
