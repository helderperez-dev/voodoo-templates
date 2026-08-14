from voodoo.components import Div, Heading, Text, Button

def page(request):
    return Div(
        Heading("Voodoo SaaS 🚀", level=1, className="text-6xl font-bold text-center mt-32 tracking-tight"),
        Div(Text("The perfect starting point for your next big idea."), className="text-center text-[var(--color-text-muted)] mt-6 text-xl"),
        Div(Button("Get Started", variant="primary", className="mt-8 px-8 py-3 rounded-full font-medium"), className="flex justify-center"),
        className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]"
    )