"""First-run setup screen using an agent to guide the user."""

from pathlib import Path
from textual.screen import Screen
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, Button
from textual.binding import Binding
from textual import work
from rich.text import Text

from vindao_agents import Agent


class SetupScreen(Screen):
    """Interactive setup wizard using an agent to guide the user."""

    BINDINGS = [
        Binding("escape", "app.quit", "Quit"),
    ]

    CSS = """
    SetupScreen {
        align: center middle;
    }

    #setup-container {
        width: 80%;
        max-width: 120;
        height: auto;
        max-height: 90%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    #chat-container {
        height: 1fr;
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }

    #input-container {
        height: auto;
        layout: horizontal;
    }

    Input {
        width: 1fr;
        margin-right: 1;
    }

    Button {
        width: auto;
    }

    .message {
        margin: 1 0;
    }

    .user-message {
        color: $accent;
    }

    .agent-message {
        color: $text;
    }

    .agent-reasoning {
        color: $text-muted;
        text-style: italic;
    }

    .tool-output {
        background: $panel;
        border: solid $success;
        padding: 1;
        margin: 1 0;
    }
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.agent = None
        self.chat_text = Text("Initializing setup agent...", style="dim italic")

    def compose(self):
        """Create child widgets."""
        yield Header()
        with Container(id="setup-container"):
            yield Static("🚀 Welcome to vindao_agents!", classes="message agent-message")
            yield Static(
                "Let me help you get started. I'm an AI agent that will guide you through the setup process.",
                classes="message agent-message"
            )
            with ScrollableContainer(id="chat-container"):
                yield Static(
                    self.chat_text,
                    id="chat-content"
                )
            with Container(id="input-container"):
                yield Input(placeholder="Type your message here...", id="user-input")
                yield Button("Send", variant="primary", id="send-button")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the setup agent when the screen is mounted."""
        self.init_agent()

    @work(exclusive=True, thread=True)
    def init_agent(self) -> None:
        """Initialize the setup agent in a background thread."""
        # Create a simple setup agent
        # TODO: Load from embedded defaults or create dynamically
        behavior = """You are a friendly setup assistant for the vindao_agents system.

Your goal is to help users understand and set up their agent system. You should:
1. Explain that agents are AI assistants configured via markdown files
2. Explain that tools are Python functions agents can call
3. Help them create their first custom agent by asking what they want it to do
4. Create agent files in ~/.vindao_agents/agents/
5. When setup is complete, say "Setup complete!" clearly

IMPORTANT CONVENTIONS:
- Tool functions MUST use snake_case naming (e.g., read_file, write_file, get_data)
- Never use camelCase (readFile, writeFile) - this is incorrect
- Keep tools simple and focused on one task
- Include docstrings with Args and Returns sections

Be conversational, helpful, and concise. Guide them through each step."""

        self.agent = Agent(
            provider=self.config.get("default_provider", "openai"),
            model=self.config.get("default_model", "gpt-4.1-nano"),
            tools=["vindao_agents.tui.setup_tools"],  # Will create this
            behavior=behavior,
            auto_save=False
        )

        # Send initial instruction
        self.app.call_from_thread(self.add_agent_message, "I'm ready! What would you like to know about the agent system, or shall we create your first agent?")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button press."""
        if event.button.id == "send-button":
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "user-input":
            self.send_message()

    def send_message(self) -> None:
        """Send user message and get agent response."""
        input_widget = self.query_one("#user-input", Input)
        message = input_widget.value.strip()

        if not message:
            return

        # Clear input
        input_widget.value = ""

        # Add user message to chat
        self.add_user_message(message)

        # Process with agent in background
        self.process_agent_response(message)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the chat display."""
        self.chat_text.append("\n\nYou: ", style="bold cyan")
        self.chat_text.append(content)

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)

        # Scroll to bottom
        container = self.query_one("#chat-container", ScrollableContainer)
        container.scroll_end(animate=False)

    def add_agent_message(self, content: str) -> None:
        """Add an agent message to the chat display."""
        self.chat_text.append("\n\nAgent: ", style="bold green")
        self.chat_text.append(content)

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)

        # Check if setup is complete
        if "setup complete" in content.lower():
            self.complete_setup()

        # Scroll to bottom
        container = self.query_one("#chat-container", ScrollableContainer)
        container.scroll_end(animate=False)

    def add_tool_output(self, tool_name: str, output: str) -> None:
        """Add tool output to the chat display."""
        self.chat_text.append(f"\n\n[Tool: {tool_name}]\n", style="bold magenta")
        self.chat_text.append(output, style="dim")

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)

        # Scroll to bottom
        container = self.query_one("#chat-container", ScrollableContainer)
        container.scroll_end(animate=False)

    @work(exclusive=True, thread=True)
    def process_agent_response(self, message: str) -> None:
        """Process agent response in background thread."""
        if not self.agent:
            return

        accumulated_content = ""

        for chunk, chunk_type in self.agent.instruct(message):
            if chunk_type == "content":
                accumulated_content += chunk
            elif chunk_type == "tool":
                # Tool execution
                self.app.call_from_thread(self.add_tool_output, chunk.name, chunk.result)

        # Display complete message
        if accumulated_content:
            self.app.call_from_thread(self.add_agent_message, accumulated_content)

    def complete_setup(self) -> None:
        """Mark setup as complete and transition to home screen."""
        self.config.mark_setup_complete()
        # Import here to avoid circular dependency
        from .home import HomeScreen
        self.app.switch_screen(HomeScreen(self.config))
