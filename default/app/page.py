from voodoo.components import Div, Heading, Text

def page(request):
    return Div(
        Heading("Hello, Voodoo! 🪄", level=1, className="text-5xl font-bold text-center mt-32 tracking-tight"),
        Div(Text("Welcome to the default template."), className="text-center text-[var(--color-text-muted)] mt-6 text-lg"),
        className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]"
    )
