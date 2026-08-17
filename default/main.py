from voodoo import A, App, Div, Heading, Text, page

app = App()


@page("/")
def home():
    return Div(
        # Deep charcoal background
        Div(className="fixed inset-0 bg-[#0A0A0A] -z-20"),
        # Ambient liquid glass glows
        Div(className="fixed top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-purple-900/20 blur-[120px] rounded-full pointer-events-none -z-10"),
        Div(className="fixed bottom-[-10%] left-1/4 w-[600px] h-[400px] bg-blue-900/10 blur-[100px] rounded-full pointer-events-none -z-10"),
        # Main Layout
        Div(
            # Premium Glass Card
            Div(
                Heading(
                    "Hello, Voodoo!",
                    level=1,
                    className="text-5xl md:text-7xl font-semibold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 tracking-tight pb-2",
                ),
                Div(
                    Text("Welcome to the default template. "),
                    Text("Ready to build something amazing?", className="text-white/40 block mt-1"),
                    className="text-center text-white/70 mt-6 text-lg md:text-xl font-medium max-w-xl mx-auto leading-relaxed",
                ),
                # Action Buttons
                Div(
                    A(
                        "Get Started",
                        href="https://github.com/helderperez-dev/voodoo",
                        target="_blank",
                        className="bg-white/10 hover:bg-white/20 text-white border border-white/10 px-8 py-3.5 rounded-full font-medium transition-all duration-300 backdrop-blur-md shadow-[0_0_15px_rgba(255,255,255,0.05)] text-center cursor-pointer",
                    ),
                    A(
                        "View Documentation",
                        href="https://github.com/helderperez-dev/voodoo#readme",
                        target="_blank",
                        className="bg-transparent hover:bg-white/5 text-white/60 px-8 py-3.5 rounded-full font-medium transition-all duration-300 text-center cursor-pointer",
                    ),
                    className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-12 w-full",
                ),
                # Card Glass Styling
                className="relative z-10 w-full max-w-4xl mx-auto mt-32 p-12 md:p-24 rounded-[2.5rem] bg-[#121212]/40 border border-white/[0.08] shadow-[0_8px_32px_0_rgba(0,0,0,0.4)] backdrop-blur-2xl flex flex-col items-center justify-center",
            ),
            className="px-6 relative flex flex-col items-center",
        ),
        className="min-h-screen font-sans text-white overflow-x-hidden selection:bg-purple-500/30",
    )


if __name__ == "__main__":
    app.run()
