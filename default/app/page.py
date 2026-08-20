"""Home route — app/page.py maps to / via folder-based routing.

A minimalist starter that shows what Voodoo gives you out of the box: build
the whole UI in Python, let folders drive your routes, and theme every
component through `--vd-*` design tokens.
"""
from voodoo import A, Badge, Button, Card, Div, Flex, Grid, Heading, Page, Stack, Text
from voodoo.seo import SEO
from voodoo.ui import Img


def _brand_logo(class_: str = "") -> Flex:
    """White wordmark for dark mode + black wordmark for light mode."""
    return Flex(
        Img(
            src="/public/voodoo-logo-white.png",
            alt="Voodoo",
            class_=f"brand-logo brand-logo--on-dark {class_}".strip(),
        ),
        Img(
            src="/public/voodoo-logo-black.png",
            alt="Voodoo",
            class_=f"brand-logo brand-logo--on-light {class_}".strip(),
        ),
    )


def _feature(badge: str, title: str, body: str) -> Card:
    """A capability card: eyebrow badge, heading, and muted description."""
    return Card(
        Stack(
            Badge(badge, variant="secondary"),
            Heading(title, level=3),
            Text(body, tone="muted"),
            gap="sm",
        ),
        class_="feature-card",
    )


def page(request):
    seo = SEO(
        title="Voodoo",
        description="A minimalist Voodoo starter — Python UI, folder routing, "
        "and themeable design tokens.",
    )

    nav = Flex(
        _brand_logo(),
        Flex(
            A("About", href="/about"),
            A("Users", href="/users/42"),
            Button(
                "Get started",
                variant="primary",
                size="sm",
                onclick="location.href='/about'",
            ),
            direction="row",
            items="center",
            gap="lg",
        ),
        justify="between",
        items="center",
        class_="site-nav",
    )

    hero = Stack(
        _brand_logo("brand-logo--hero"),
        Heading("Build your UI in Python", level=1, size="display"),
        Text(
            "One runtime for web, APIs, agents, workers, and realtime — "
            "rendered with semantic components and themeable tokens.",
            tone="muted",
        ),
        Flex(
            Button(
                "Get started",
                variant="primary",
                size="lg",
                onclick="location.href='/about'",
            ),
            A("View a dynamic route →", href="/users/42"),
            direction="row",
            justify="center",
            items="center",
            gap="md",
        ),
        items="center",
        gap="lg",
        class_="hero",
    )

    features = Grid(
        _feature(
            "Routing",
            "Folder-based",
            "app/page.py → /. Drop app/about/page.py and /about exists — "
            "zero wiring.",
        ),
        _feature(
            "Components",
            "Semantic UI",
            "Button, Card, Grid, Stack… emit vd-* classes resolved by your "
            "theme tokens.",
        ),
        _feature(
            "Theming",
            "Tokens, not CSS",
            "Change a --vd-* token and every component restyles instantly, "
            "dark or light.",
        ),
        _feature(
            "Realtime",
            "Mesh events",
            "A websocket bus streams DOM patches to every connected client, "
            "live.",
        ),
        _feature(
            "Workers",
            "Durable tasks",
            "Decorate a function with @task and run it on a background queue.",
        ),
        _feature(
            "Agents",
            "AI, optional",
            "Agents hold capabilities and execute intents — AI is compute, "
            "never required.",
        ),
        cols="3",
        gap="md",
    )

    footer = Flex(
        Text("Built with Voodoo", tone="muted"),
        A(
            "GitHub",
            href="https://github.com/helderperez-dev/voodoo",
            target="_blank",
        ),
        justify="between",
        items="center",
        class_="site-footer",
    )

    ui = Div(
        nav,
        Page(
            Stack(
                hero,
                features,
                gap="xxl",
            )
        ),
        footer,
    )

    return seo, ui
