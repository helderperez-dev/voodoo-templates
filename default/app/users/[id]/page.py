"""User route — app/users/[id]/page.py maps to /users/{id}.

Bracket folders create dynamic segments; the `id: int` annotation coerces
the path segment to the declared type.
"""
from voodoo import Card, Heading, Page, Text
from voodoo.seo import SEO


def page(request, id: int):
    seo = SEO(title=f"User {id} — My Voodoo App")
    ui = Page(
        Card(
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
        )
    )
    return seo, ui
