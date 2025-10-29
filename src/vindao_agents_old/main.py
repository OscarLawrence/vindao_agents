"""Main entry point for vindao_agents CLI."""

def main():
    """Launch the vindao_agents TUI."""
    from .tui import TUIApp

    app = TUIApp()
    app.run()


if __name__ == "__main__":
    main()
