"""Default Voodoo workbench.

The starter app is intentionally useful: it exercises the public UI, reactive
rendering, Python event handlers, and the Store-native Model API against the
same ``.voodoo/application.vstore`` used by the Runtime.
"""

from voodoo import Model
from voodoo.seo import SEO
from voodoo.ui import (
    Badge,
    Button,
    Card,
    Container,
    Divider,
    Flex,
    Grid,
    Heading,
    Page,
    Stack,
    Text,
    ThemeToggle,
)
from voodoo.ui.state import state


class StoreProbe(Model):
    """Small persistent record used to exercise Voodoo Store."""

    name: str
    status: str
    runs: int


_revision = state(0)


async def create_record() -> None:
    """Exercise create + generated ids + reactive rerender."""
    next_number = await StoreProbe.count() + 1
    await StoreProbe.create(
        name=f"Persistent record {next_number}",
        status="healthy",
        runs=1,
    )
    _revision.update(lambda value: value + 1)


async def update_latest() -> None:
    """Exercise ordered queries + update/save."""
    records = await StoreProbe.where().order_by("-id").limit(1)
    if records:
        record = records[0]
        record.status = "attention" if record.status == "healthy" else "healthy"
        record.runs += 1
        await record.save()
        _revision.update(lambda value: value + 1)


async def delete_latest() -> None:
    """Exercise get/query + delete."""
    records = await StoreProbe.where().order_by("-id").limit(1)
    if records:
        await records[0].delete()
        _revision.update(lambda value: value + 1)


async def clear_records() -> None:
    """Exercise scans and repeated deletes without a SQL fallback."""
    for record in await StoreProbe.all():
        await record.delete()
    _revision.update(lambda value: value + 1)


def metric(label: str, value: str, detail: str, *, tone: str | None = None) -> Card:
    return Card(
        Stack(
            Text(label, tone="muted"),
            Heading(value, level=2, size="lg", tone=tone),
            Text(detail, tone="muted"),
            gap="xs",
        ),
        css={"padding": "1.35rem"},
    )


def record_card(record: StoreProbe) -> Card:
    variant = "success" if record.status == "healthy" else "warning"
    return Card(
        Flex(
            Stack(
                Text(f"#{record.id}", tone="muted"),
                Heading(record.name, level=3, size="sm"),
                Text(f"Persisted updates: {record.runs}", tone="muted"),
                gap="xs",
            ),
            Badge(record.status, variant=variant),
            justify="between",
            items="start",
            gap="md",
        ),
        css={"padding": "1rem 1.1rem"},
    )


async def page(request):
    """Render a living diagnostic surface for the Runtime and Store."""
    # Reading this cell binds the page to Voodoo's reactive render graph. Every
    # successful Store mutation increments it and patches the page over WS.
    _revision.get()

    records = await StoreProbe.where().order_by("-id").limit(8)
    total = await StoreProbe.count()
    healthy = await StoreProbe.count(status="healthy")
    attention = await StoreProbe.count(status="attention")

    seo = SEO(
        title="Voodoo Workbench",
        description="A live diagnostic app for the Voodoo Runtime and Store.",
    )

    ui = Page(
        Container(
            Stack(
                Flex(
                    Stack(
                        Badge("VOODOO  /  LOCAL RUNTIME", variant="default"),
                        Heading("Runtime Workbench", level=1, size="display"),
                        Text(
                            "A real starter app that proves persistence, reactivity, "
                            "Python events and the default Store instead of rendering "
                            "a static hello-world page.",
                            tone="muted",
                        ),
                        gap="sm",
                    ),
                    ThemeToggle(),
                    justify="between",
                    items="start",
                    gap="lg",
                ),
                Grid(
                    metric(
                        "Runtime",
                        "online",
                        "HTTP + WebSocket lifecycle is active",
                        tone="success",
                    ),
                    metric(
                        "Store records",
                        str(total),
                        ".voodoo/application.vstore",
                    ),
                    metric(
                        "Query health",
                        f"{healthy}/{total}",
                        f"{attention} record(s) need attention",
                        tone="primary",
                    ),
                    cols="3",
                    gap="4",
                ),
                Card(
                    Stack(
                        Flex(
                            Stack(
                                Heading("Store playground", level=2, size="md"),
                                Text(
                                    "These controls execute real Model operations. "
                                    "Reload or restart Voodoo to verify persistence.",
                                    tone="muted",
                                ),
                                gap="xs",
                            ),
                            Badge("Store-first", variant="success"),
                            justify="between",
                            items="start",
                            gap="md",
                        ),
                        Divider(),
                        Flex(
                            Button(
                                "Create persistent record",
                                on_click=create_record,
                                variant="primary",
                            ),
                            Button(
                                "Update latest",
                                on_click=update_latest,
                                variant="secondary",
                            ),
                            Button(
                                "Delete latest",
                                on_click=delete_latest,
                                variant="secondary",
                            ),
                            Button(
                                "Clear",
                                on_click=clear_records,
                                variant="secondary",
                            ),
                            wrap="wrap",
                            gap="sm",
                        ),
                    ),
                    css={"padding": "1.4rem"},
                ),
                Stack(
                    Flex(
                        Heading("Persisted records", level=2, size="md"),
                        Text("latest 8", tone="muted"),
                        justify="between",
                        items="center",
                    ),
                    (
                        Grid(*(record_card(record) for record in records), cols="2", gap="3")
                        if records
                        else Card(
                            Stack(
                                Heading("The Store is empty", level=3, size="sm"),
                                Text(
                                    "Create a record above. Then refresh the browser or "
                                    "restart `voodoo dev`: it should still be here.",
                                    tone="muted",
                                ),
                                gap="xs",
                            ),
                            css={"padding": "1.35rem"},
                        )
                    ),
                    gap="sm",
                ),
                Divider(),
                Flex(
                    Text(
                        "Default infrastructure: Runtime + application.vstore",
                        tone="muted",
                    ),
                    Text("No SQLite · No Redis · No external database", tone="muted"),
                    justify="between",
                    wrap="wrap",
                    gap="sm",
                ),
                gap="xl",
            )
        ),
        size="xl",
    )

    return seo, ui
