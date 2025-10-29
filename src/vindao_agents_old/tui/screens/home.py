"""Home screen showing agent selector and dashboard."""

from pathlib import Path
import json
from datetime import datetime
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Button, TabbedContent, TabPane
from textual.binding import Binding


class HomeScreen(Screen):
    """Main dashboard for selecting agents and managing the system."""

    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("n", "new_agent", "New Agent"),
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "app.quit", "Quit"),
    ]

    CSS = """
    HomeScreen {
        align: center middle;
    }

    #home-container {
        width: 80%;
        max-width: 100;
        height: auto;
        max-height: 80%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        color: $accent;
        margin: 1 0;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin: 0 0 2 0;
    }

    TabbedContent {
        height: 1fr;
    }

    ListView {
        height: 1fr;
        border: solid $accent;
        margin: 1 0;
    }

    ListItem {
        padding: 1;
    }

    .session-info {
        color: $text-muted;
        text-style: italic;
    }

    #button-container {
        layout: horizontal;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .empty-state {
        text-align: center;
        color: $text-muted;
        padding: 4 2;
    }
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def compose(self):
        """Create child widgets."""
        yield Header()
        with Container(id="home-container"):
            yield Static("vindao agents", id="title")
            yield Static("Select an agent or resume a session", id="subtitle")

            with TabbedContent():
                with TabPane("Agents", id="agents-tab"):
                    agent_files = self.config.get_agent_files()
                    if agent_files:
                        with ListView(id="agent-list"):
                            for agent_file in agent_files:
                                yield ListItem(Label(f"📝 {agent_file.stem}"))
                    else:
                        yield Static(
                            "No agents found.\n\nCreate your first agent to get started!",
                            classes="empty-state"
                        )

                with TabPane("Sessions", id="sessions-tab"):
                    sessions = self._get_recent_sessions()
                    if sessions:
                        with ListView(id="session-list"):
                            for session in sessions:
                                session_label = f"💬 {session['agent_name']} - {session['time_ago']}"
                                yield ListItem(Label(session_label), id=f"session-{session['session_id']}")
                    else:
                        yield Static(
                            "No sessions found.\n\nStart chatting with an agent to create a session!",
                            classes="empty-state"
                        )

            with Horizontal(id="button-container"):
                yield Button("New Agent", variant="primary", id="new-agent-btn")
                yield Button("Settings", variant="default", id="settings-btn")
                yield Button("Quit", variant="error", id="quit-btn")

        yield Footer()

    def _get_recent_sessions(self, limit: int = 10) -> list[dict]:
        """Get recent sessions sorted by last update time."""
        sessions_dir = self.config.sessions_dir
        if not sessions_dir.exists():
            return []

        sessions = []
        for session_file in sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    config_data = data.get("config", {})
                    state_data = data.get("state", {})

                    # Get agent name from the behavior or use model as fallback
                    agent_name = config_data.get("model", "Unknown")
                    updated_at = state_data.get("updated_at", 0)

                    # Calculate time ago
                    time_ago = self._format_time_ago(updated_at)

                    sessions.append({
                        "session_id": state_data.get("session_id"),
                        "agent_name": agent_name,
                        "updated_at": updated_at,
                        "time_ago": time_ago,
                        "message_count": len(state_data.get("messages", []))
                    })
            except Exception:
                continue

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions[:limit]

    def _format_time_ago(self, timestamp: float) -> str:
        """Format timestamp as human-readable time ago."""
        now = datetime.now().timestamp()
        diff = int(now - timestamp)

        if diff < 60:
            return "just now"
        elif diff < 3600:
            mins = diff // 60
            return f"{mins}m ago"
        elif diff < 86400:
            hours = diff // 3600
            return f"{hours}h ago"
        else:
            days = diff // 86400
            return f"{days}d ago"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "quit-btn":
            self.app.exit()
        elif event.button.id == "new-agent-btn":
            self.action_new_agent()
        elif event.button.id == "settings-btn":
            # TODO: Implement settings screen
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from either agents or sessions list."""
        if event.list_view.id == "agent-list":
            agent_files = self.config.get_agent_files()
            if event.list_view.index is not None and event.list_view.index < len(agent_files):
                selected_agent = agent_files[event.list_view.index]
                self.open_chat(selected_agent)
        elif event.list_view.id == "session-list":
            # Get the selected item's ID to extract session_id
            selected_item = event.item
            if selected_item and selected_item.id and selected_item.id.startswith("session-"):
                session_id = selected_item.id.replace("session-", "")
                self.resume_session(session_id)

    def open_chat(self, agent_file: Path) -> None:
        """Open chat screen with selected agent."""
        from .chat import ChatScreen
        self.app.push_screen(ChatScreen(self.config, agent_file))

    def resume_session(self, session_id: str) -> None:
        """Resume an existing session."""
        from .chat import ChatScreen
        self.app.push_screen(ChatScreen(self.config, None, session_id=session_id))

    def action_new_agent(self) -> None:
        """Create a new agent."""
        # TODO: Implement agent creation wizard
        # For now, show a placeholder
        self.notify("Agent creation wizard coming soon!", severity="information")

    def action_refresh(self) -> None:
        """Refresh the screen."""
        self.app.pop_screen()
        self.app.push_screen(HomeScreen(self.config))
