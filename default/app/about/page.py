"""About route — app/about/page.py maps to /about."""
from voodoo import Container, Heading, Page, Text
from voodoo.seo import SEO


def page(request):
    seo = SEO(title="About — My Voodoo App", description="About this project.")
    ui = Page(
        Container(
            Heading("About", level=1, size="xl"),
            Text("This route is defined by app/about/page.py.", tone="muted"),
            Text(
                "Folder structure drives routing: app/about/page.py → /about.",
                tone="muted",
            ),
        )
    )
    return seo, ui
