"""Home route — app/page.py maps to / via folder-based routing.

The starter home, built entirely from Voodoo chrome components: a ``Hero``
split with a live code card, a ``Stats`` strip, the ``FeatureCard`` grid, and
a closing ``CTABand``. Everything is Python — no JS required.
"""
from voodoo import (
    Button,
    CodeBlock,
    CTABand,
    Div,
    Eyebrow,
    FeatureCard,
    Flex,
    Grid,
    Heading,
    Hero,
    LinkArrow,
    Page,
    Stack,
    Stat,
    Stats,
    Text,
)
from textwrap import dedent
from voodoo.ui.component import Html

from app._meta import page_seo, site_footer, site_nav

# A static code sample. ``CodeBlock`` escapes HTML for safety, so syntax
# highlighting is opt-in: pass ``Html`` children with ``.tok-*`` spans whose
# colors map to the theme's ``--vd-code-*`` tokens (see .voodoo/theme/custom.css).
_CODE_CARD = Html(dedent("""
    <span class="tok-com"># app/page.py → &quot;/&quot;</span>
    <span class="tok-kw">from</span> voodoo <span class="tok-kw">import</span> Agent, Page, Text, tool

    <span class="tok-kw">@tool</span>
    <span class="tok-kw">async def</span> <span class="tok-fn">create_lead</span>(name, email):
        <span class="tok-kw">return await</span> Lead.create(name, email)

    agent = Agent(model=<span class="tok-str">&quot;gpt-4o&quot;</span>, tools=[<span class="tok-str">&quot;create_lead&quot;</span>])

    <span class="tok-kw">def</span> <span class="tok-fn">page</span>(request):
        <span class="tok-kw">return</span> Page(Text(<span class="tok-str">&quot;One runtime.&quot;</span>))
    """).strip())


def code_card() -> Div:
    """A terminal window: chrome bar over a native ``CodeBlock``."""
    return Div(
        Flex(
            Html('<span class="code-dots"><i></i><i></i><i></i></span>'),
            Text("app/page.py", class_="code-file"),
            Text("live", class_="code-live"),
            justify="between",
            items="center",
            class_="code-card__bar",
        ),
        Div(
            CodeBlock(_CODE_CARD, language="python", class_="code-card__code"),
            class_="code-card__body",
        ),
        class_="code-card",
    )


def _feature(num: str, title: str, body: str) -> FeatureCard:
    """A capability card: mono index, display heading, muted description."""
    return FeatureCard(
        Stack(
            Text(num, class_="feature-num"),
            Heading(title, level=3),
            Text(body, tone="muted"),
            gap="sm",
        )
    )


def _step(num: str, title: str, command: str, body: str) -> FeatureCard:
    """A quickstart step: index, heading, a mono command chip, description."""
    return FeatureCard(
        Stack(
            Text(num, class_="feature-num"),
            Heading(title, level=3),
            Text(command, class_="step-cmd"),
            Text(body, tone="muted"),
            gap="sm",
        )
    )


def page(request):
    seo = page_seo(
        "Voodoo — The programmable runtime",
        "One runtime for adaptive applications and operational systems. Web, "
        "APIs, agents, workers, and realtime events — first-class Python "
        "primitives, wired together with zero glue.",
    )

    nav = site_nav()

    hero = Hero(
        Grid(
            Stack(
                Flex(
                    Html('<span class="badge-dot"></span>'),
                    Text("Voodoo 1.18 · the programmable runtime", tone="muted"),
                    direction="row",
                    items="center",
                    gap="sm",
                    class_="hero-badge",
                ),
                Eyebrow("app/page.py → /"),
                Heading(
                    "One runtime for ",
                    Html('<span class="accent-italic">adaptive</span>'),
                    " software.",
                    level=1,
                    class_="hero-title",
                ),
                Text(
                    "Web, APIs, agents, workers, and realtime events — first-class "
                    "primitives in one Python runtime, sharing one execution model. "
                    "Composition over configuration. No build step, no glue, no ceremony.",
                    class_="hero-sub",
                ),
                Flex(
                    Button(
                        "Get started",
                        variant="primary",
                        size="lg",
                        onclick="location.href='/about'",
                    ),
                    LinkArrow("View a dynamic route", href="/users/42"),
                    direction="row",
                    items="center",
                    gap="md",
                    wrap="wrap",
                ),
                Flex(
                    Html('<span class="hint-prompt">$</span>'),
                    Text("pip install voodoo-framework", class_="hint-cmd"),
                    class_="hint-pill",
                ),
                gap="lg",
                items="start",
            ),
            code_card(),
            cols="2",
            gap="0",
            class_="hero-grid",
        )
    )

    stats = Stats(
        Stat("0", "config files to start"),
        Stat("1", "runtime, not a stack"),
        Stat("100%", "python, zero js"),
        Stat("∞", "events, one mesh"),
        cols=4,
    )

    features = Stack(
        Stack(
            Eyebrow("The runtime"),
            Heading("Everything is a primitive.", level=2, class_="section-title"),
            Text(
                "UI, agents, workers, data, and events — first-class and wired "
                "together from the first line.",
                class_="section-sub",
            ),
            gap="md",
            items="start",
        ),
        Grid(
            _feature(
                "01",
                "Agents as primitives",
                "Agent() sits next to Button() and Card(). AI is one form of "
                "compute — never a separate subsystem.",
            ),
            _feature(
                "02",
                "Voodoo Mesh",
                "A unified event layer connects UI, workers, agents, and apps — "
                "events over tightly-coupled calls.",
            ),
            _feature(
                "03",
                "One tool, many consumers",
                "A single @tool definition serves Python calls, agents, MCP "
                "servers, and the mesh.",
            ),
            _feature(
                "04",
                "Human-in-the-loop",
                "ask_human() + approve()/deny() — humans are compute "
                "participants, not afterthoughts.",
            ),
            _feature(
                "05",
                "Durable by default",
                "Tasks, executions, schedules, and events survive restarts — "
                "SQLite out of the box.",
            ),
            _feature(
                "06",
                "Adaptive execution",
                "A planner resolves capabilities; a supervisor steers retry, "
                "fallback, and budget.",
            ),
            cols="3",
            gap="md",
        ),
        gap="xl",
        class_="section",
    )

    quickstart = Stack(
        Stack(
            Eyebrow("Quickstart"),
            Heading("Zero to a live route in seconds", level=2, class_="section-title"),
            Text(
                "Three commands and you're running. No config, no build step.",
                class_="section-sub",
            ),
            gap="md",
            items="start",
        ),
        Grid(
            _step(
                "01",
                "Install",
                "pip install voodoo-framework",
                "One package pulls in the entire runtime.",
            ),
            _step(
                "02",
                "Scaffold",
                "voodoo new my-app",
                "Generates this starter — routes, theme, and all.",
            ),
            _step(
                "03",
                "Run",
                "voodoo dev",
                "Live reload on http://localhost:8000, instantly.",
            ),
            cols="3",
            gap="md",
        ),
        gap="xl",
        class_="section",
    )

    cta = CTABand(
        Stack(
            Heading("One runtime. Zero glue.", level=2, class_="cta-title"),
            Text(
                "Clone the starter and you're live in seconds. Add an Agent, a "
                "@task worker, or a mesh event later — same runtime, same Python.",
                class_="cta-sub",
            ),
            Flex(
                Button(
                    "Get started",
                    variant="secondary",
                    size="lg",
                    onclick="location.href='/about'",
                ),
                Button(
                    "Read the docs",
                    variant="outline",
                    size="lg",
                    onclick="location.href='/docs'",
                ),
                LinkArrow("Meet the dynamic route", href="/users/42"),
                direction="row",
                items="center",
                gap="md",
                wrap="wrap",
            ),
            gap="lg",
            items="start",
        )
    )

    ui = Div(
        nav,
        Page(
            Stack(
                hero,
                stats,
                features,
                quickstart,
                cta,
                gap="0",  # sections carry their own rhythm
            )
        ),
        site_footer(),
    )

    return seo, ui
