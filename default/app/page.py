"""Home route — app/page.py maps to / via folder-based routing.

Voodoo CSS is the default style adapter: components emit semantic `vd-*`
classes (e.g. `vd-button vd-button--primary`) resolved by theme tokens, so
prefer semantic props (`variant`, `size`, `tone`) over utility classes.
"""
from voodoo import A, Button, Card, Flex, Heading, Page, Stack, Text
from voodoo.seo import SEO


def page(request):
    seo = SEO(
        title="My Voodoo App",
        description="Built with Voodoo: Python UI, semantic components, themeable tokens.",
    )
    ui = Page(
        Stack(
            Heading("Hello, Voodoo", level=1, size="xl"),
            Text(
                "Build your UI in Python. Voodoo CSS ships themed, semantic "
                "components out of the box.",
                tone="muted",
            ),
            Flex(
                Button("Get Started", variant="primary"),
                A(
                    "View about",
                    href="/about",
                    onClick="voodoo.navigate('/about')",
                ),
                direction="row",
                gap="sm",
            ),
            Card(
                Heading("Folder-based routing", level=3),
                Text("This page lives at app/page.py and maps to /."),
                Text(
                    "Add app/about/page.py to create /about — no extra wiring.",
                    tone="muted",
                ),
            ),
            gap="lg",
        )
    )
    return seo, ui
