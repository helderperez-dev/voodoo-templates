"""Shared page chrome for the starter — safe to keep in ``app/``.

Folder-based routing only imports modules that define a ``page()`` callable,
so a plain helper module like this one is never registered as a route.

Everything here is pure Voodoo components — the native ``Navbar`` chrome
(logo, ``NavLink``s, ``ThemeToggle``), the footer, and a page-level ``SEO``
factory. The default theme is zero-network and uses the system font stack, so
no webfonts are injected here.
"""

from voodoo import (
    A,
    Brand,
    Button,
    Divider,
    Flex,
    Img,
    Navbar,
    NavLink,
    Stack,
    Text,
    ThemeToggle,
)
from voodoo.seo import OpenGraph, SEO
from voodoo.ui.component import Html

_GH_URL = "https://github.com/helderperez-dev/voodoo"


def page_seo(title: str, description: str) -> SEO:
    """Page metadata with shared Open Graph defaults.

    The default theme is zero-network — it uses the system font stack and
    loads no webfonts, so there is no ``extra_head`` font injection here.
    """
    return SEO(
        title=title,
        description=description,
        og=OpenGraph(
            title=title,
            description=description,
            type="website",
            site_name="Voodoo",
        ),
    )


def _brand_logo() -> Brand:
    """The Voodoo wordmark, rendered once and tinted for the active theme.

    A single black mark is served from ``/public``; ``custom.css`` inverts it
    to white when ``html.dark`` is present (mirroring the framework's theme
    toggle), so there is no duplicate image element in the DOM.
    """
    return Brand(
        Img(
            src="/public/voodoo-logo-black.png",
            alt="Voodoo",
            class_="brand-logo",
        ),
    )


def _nav_links(active: str) -> list[NavLink]:
    """Fresh ``NavLink`` instances — each render must be a unique DOM node."""
    return [
        NavLink("About", href="/about", active=active == "about"),
        NavLink("Users", href="/users/42", active=active == "users"),
        NavLink("GitHub", href=_GH_URL, target="_blank"),
    ]


def site_nav(active: str = "") -> Navbar:
    """Sticky top bar with a desktop link row and an animated mobile menu.

    The mobile menu is driven by a CSS-only checkbox (``#nav-toggle``) — no
    JavaScript — so it slides open/closed and the hamburger collapses into an
    ✕. ``custom.css`` wires the ``:checked`` state to both the dropdown sheet
    and the icon, and hides the whole thing above the ``md`` breakpoint.
    """
    return Navbar(
        Html(
            '<input type="checkbox" id="nav-toggle" class="nav-toggle" '
            'aria-label="Toggle navigation menu">'
        ),
        Flex(
            _brand_logo(),
            Flex(
                *_nav_links(active),
                Button(
                    "Get started",
                    variant="primary",
                    size="sm",
                    class_="nav-cta",
                    onclick="location.href='/about'",
                ),
                direction="row",
                items="center",
                gap="lg",
                class_="nav-links nav-links--desktop",
            ),
            Flex(
                ThemeToggle(),
                Html(
                    '<label for="nav-toggle" class="nav-toggle-btn" '
                    'aria-hidden="true"><span></span><span></span><span></span></label>'
                ),
                direction="row",
                items="center",
                gap="sm",
                class_="nav-actions",
            ),
            direction="row",
            items="center",
            justify="between",
            gap="md",
            class_="nav-inner",
        ),
        Stack(
            Stack(
                *_nav_links(active),
                Divider(),
                Button(
                    "Get started",
                    variant="primary",
                    size="lg",
                    class_="nav-menu-cta",
                    onclick="location.href='/about'",
                ),
                gap="xs",
                class_="nav-menu__inner",
            ),
            class_="nav-menu",
        ),
    )


def site_footer() -> Stack:
    """Footer: brand blurb, quick links, and the obligatory framework plug."""
    return Stack(
        Flex(
            Flex(
                _brand_logo(),
                Text(
                    "The programmable runtime for adaptive applications and "
                    "operational systems.",
                    class_="footer-tagline",
                ),
                direction="col",
                gap="sm",
            ),
            Flex(
                A("About", href="/about", class_="footer-link"),
                A("Users", href="/users/42", class_="footer-link"),
                A("GitHub", href=_GH_URL, target="_blank", class_="footer-link"),
                A("Docs", href="/about", class_="footer-link"),
                direction="row",
                gap="lg",
                wrap="wrap",
                class_="footer-links",
            ),
            justify="between",
            items="center",
            wrap="wrap",
            class_="footer-main",
        ),
        Flex(
            Text("© 2026 Voodoo", class_="footer-meta"),
            Text("Built with Voodoo", class_="footer-meta"),
            justify="between",
            class_="footer-bottom",
        ),
        gap="xl",
        class_="site-footer",
    )
