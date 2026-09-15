"""Default Voodoo landing page."""

from voodoo.seo import SEO
from voodoo.ui import (
    A,
    Badge,
    Box,
    Brand,
    Container,
    Flex,
    Heading,
    LinkArrow,
    Page,
    Stack,
    Text,
    ThemeToggle,
)


def page(request):
    seo = SEO(
        title="Voodoo App",
        description="A Python application powered by the Voodoo Runtime.",
    )

    ui = Page(
        Box(
            Container(
                Flex(
                    # Header
                    Flex(
                        Brand(
                            light="/voodoo-logo-black.png",
                            dark="/voodoo-logo-white.png",
                            alt="Voodoo",
                            width=180,
                            href="/",
                        ),
                        ThemeToggle(),
                        justify="between",
                        items="center",
                    ),

                    # Hero
                    Flex(
                        Stack(
                            Flex(
                                Badge(
                                    "VOODOO 2.8.2",
                                    variant="outline",
                                ),
                                justify="start",
                            ),

                            Stack(
                                Heading(
                                    "Your application",
                                    level=1,
                                    css={
                                        "font_size": "clamp(3.4rem, 5vw, 5rem)",
                                        "line_height": "0.96",
                                        "letter_spacing": "-0.055em",
                                        "font_weight": "750",
                                    },
                                ),

                                Heading(
                                    "starts here.",
                                    level=1,
                                    css={
                                        "font_size": "clamp(3.4rem, 5vw, 5rem)",
                                        "line_height": "0.96",
                                        "letter_spacing": "-0.055em",
                                        "font_weight": "750",
                                        "background": (
                                            "linear-gradient("
                                            "90deg,"
                                            "#5f6cff 0%,"
                                            "#9a5cff 48%,"
                                            "#6574ff 100%"
                                            ")"
                                        ),
                                        "background_clip": "text",
                                        "-webkit-background-clip": "text",
                                        "-webkit-text-fill-color": "transparent",
                                    },
                                ),

                                gap="sm",
                            ),

                            Text(
                                "Build with one Python runtime.",
                                tone="muted",
                                css={
                                    "font_size": "1.2rem",
                                },
                            ),

                            # Links
                            Flex(
                                LinkArrow(
                                    "Read the docs",
                                    href="https://voodoo.build",
                                ),
                                A(
                                    "GitHub",
                                    Text(
                                        "↗",
                                        css={
                                            "font_size": "1rem",
                                            "line_height": "1",
                                        },
                                    ),
                                    href=(
                                        "https://github.com/"
                                        "helderperez-dev/voodoo"
                                    ),
                                    target="_blank",
                                    css={
                                        "display": "inline-flex",
                                        "align_items": "center",
                                        "gap": "0.35rem",
                                        "font_size": "1rem",
                                        "font_weight": "500",
                                        "color": "var(--vd-color-primary)",
                                        "text_decoration": "none",
                                        "line_height": "1",
                                    },
                                ),
                                gap="lg",
                                items="center",
                            ),

                            # Getting started hint
                            Box(
                                Flex(
                                    Text(
                                        ">_",
                                        tone="muted",
                                        css={
                                            "font_family": "var(--vd-font-mono)",
                                        },
                                    ),
                                    Text(
                                        "Edit",
                                        tone="muted",
                                        css={
                                            "font_family": "var(--vd-font-mono)",
                                        },
                                    ),
                                    Text(
                                        "app/page.py",
                                        css={
                                            "font_family": "var(--vd-font-mono)",
                                            "background": (
                                                "color-mix("
                                                "in srgb,"
                                                "var(--vd-color-text) 7%,"
                                                "transparent"
                                                ")"
                                            ),
                                            "padding": "0.3rem 0.5rem",
                                            "border_radius": "0.4rem",
                                        },
                                    ),
                                    Text(
                                        "to get started.",
                                        tone="muted",
                                        css={
                                            "font_family": "var(--vd-font-mono)",
                                        },
                                    ),
                                    gap="sm",
                                    items="center",
                                    wrap="wrap",
                                ),
                                css={
                                    "border_top": (
                                        "1px solid "
                                        "var(--vd-color-border-soft)"
                                    ),
                                    "padding_top": "1.2rem",
                                    "margin_top": "0.5rem",
                                    "max_width": "35rem",
                                },
                            ),

                            gap="lg",
                            css={
                                "max_width": "58rem",
                            },
                        ),

                        items="center",
                        css={
                            "flex": "1",
                            "min_height": "0",
                        },
                    ),

                    # Footer
                    Flex(
                        Text(
                            "Voodoo · Python runtime for adaptive applications",
                            tone="muted",
                            css={
                                "font_size": "0.85rem",
                            },
                        ),
                        Text(
                            "v2.8.2",
                            tone="muted",
                            css={
                                "font_size": "0.85rem",
                            },
                        ),
                        justify="between",
                        items="center",
                        wrap="wrap",
                    ),

                    direction="col",
                    css={
                        "height": "100dvh",
                        "padding_top": "2.25rem",
                        "padding_bottom": "1.5rem",
                    },
                ),
                size="xl",
            ),

            # Organic ambient background
            css={
                "height": "100dvh",
                "overflow": "hidden",
                "background": (
                    "linear-gradient("
                    "118deg,"
                    "rgba(124,58,237,0.18) 0%,"
                    "rgba(99,102,241,0.09) 14%,"
                    "rgba(124,58,237,0.035) 31%,"
                    "transparent 48%"
                    "),"
                    "linear-gradient("
                    "325deg,"
                    "rgba(99,102,241,0.12) 0%,"
                    "rgba(168,85,247,0.065) 16%,"
                    "rgba(99,102,241,0.025) 34%,"
                    "transparent 52%"
                    "),"
                    "linear-gradient("
                    "205deg,"
                    "transparent 0%,"
                    "transparent 52%,"
                    "rgba(124,58,237,0.045) 70%,"
                    "transparent 88%"
                    "),"
                    "var(--vd-color-background)"
                ),
            },
        ),
        size="full",
        pad=False,
    )

    return seo, ui
