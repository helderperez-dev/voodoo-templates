"""Default Voodoo route — intentionally small and stable."""

from voodoo.ui import A, Button, Container, Heading, Page, Stack, Text
from voodoo.seo import SEO


def page(request):
    """Render the home page using stable public UI primitives."""
    seo = SEO(
        title="Voodoo App",
        description="A minimal application powered by the Voodoo Runtime.",
    )

    ui = Page(
        Container(
            Stack(
                Heading("Hello, Voodoo", level=1),
                Text(
                    "One Runtime. One local Store. No external infrastructure required.",
                    tone="muted",
                ),
                Button("Get started", variant="primary"),
                A(
                    "Voodoo on GitHub",
                    href="https://github.com/helderperez-dev/voodoo",
                    target="_blank",
                ),
                gap="md",
            )
        )
    )

    return seo, ui
