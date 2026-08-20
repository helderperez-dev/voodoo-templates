"""User route — app/users/[id]/page.py maps to /users/{id}.

Bracket folders create dynamic segments; the `id: int` annotation coerces
the path segment to the declared type.
"""
from voodoo import A, Badge, Card, Container, Heading, Page, Stack, Text
from voodoo.seo import SEO


def page(request, id: int):
    seo = SEO(
        title=f"User {id} — Voodoo App",
        description=f"Dynamic route /users/{id}.",
    )
    ui = Page(
        Container(
            Card(
                Stack(
                    Badge(f"users/{id}", variant="secondary"),
                    Heading(f"User #{id}", level=2),
                    Text(
                        "Dynamic segments use bracket folders: "
                        "app/users/[id]/page.py → /users/{id}.",
                        tone="muted",
                    ),
                    Text(
                        "The int annotation coerces the segment: '42' → 42.",
                        tone="muted",
                    ),
                    A("← Back home", href="/"),
                    gap="md",
                )
            )
        )
    )
    return seo, ui
