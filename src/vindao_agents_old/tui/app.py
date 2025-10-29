"""Main Textual application for vindao_agents TUI."""

from textual.app import App, ComposeResult
from textual.binding import Binding

from .config import Config
from .screens.setup import SetupScreen
from .screens.home import HomeScreen


class TUIApp(App):
    """Interactive TUI for managing and chatting with agents."""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.title = "vindao agents"
        self.sub_title = "Minimal AI Agent System"

    def on_mount(self) -> None:
        """Called when app is mounted - decide which screen to show."""
        self.config.ensure_directories()

        if self.config.is_first_run():
            self.push_screen(SetupScreen(self.config))
        else:
            self.push_screen(HomeScreen(self.config))

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def run():
    """Entry point for the TUI application."""
    app = TUIApp()
    app.run()
