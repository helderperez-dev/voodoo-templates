"""About route — app/about/page.py maps to /about."""
from voodoo import A, Badge, Card, Container, Heading, Page, Stack, Text
from voodoo.seo import SEO


def page(request):
    seo = SEO(title="About — Voodoo App", description="How folder-based routing works.")
    ui = Page(
        Container(
            Stack(
                Badge("Routing", variant="secondary"),
                Heading("About", level=1, size="xl"),
                Text(
                    "This route is defined by app/about/page.py and maps to /about.",
                    tone="muted",
                ),
                Card(
                    Stack(
                        Heading("The folder is the router", level=3),
                        Text(
                            "Add app/contact/page.py and /contact exists — no "
                            "registration, no config. The file-based page(request) "
                            "convention returns your UI and SEO metadata.",
                            tone="muted",
                        ),
                        gap="md",
                    )
                ),
                A("← Back home", href="/"),
                gap="lg",
            )
        )
    )
    return seo, ui
