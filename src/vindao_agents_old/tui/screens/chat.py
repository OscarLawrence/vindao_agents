"""Interactive chat screen with streaming agent responses."""

from pathlib import Path
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, Button, Label
from textual.binding import Binding
from textual import work
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown

from vindao_agents import Agent
from vindao_agents.models.messages import UserMessage, AssistantMessage, ToolMessage


class ChatScreen(Screen):
    """Chat interface with streaming agent responses."""

    BINDINGS = [
        Binding("escape", "go_back", "Back to Home"),
        Binding("ctrl+l", "clear_chat", "Clear Chat"),
    ]

    CSS = """
    ChatScreen {
        layout: horizontal;
    }

    #sidebar {
        width: 30;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
        padding: 1;
    }

    #sidebar-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin: 0 0 1 0;
    }

    #agent-info {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
        height: auto;
    }

    #tools-container {
        border: solid $success;
        padding: 1;
        height: 1fr;
        margin: 1 0;
    }

    .tool-item {
        color: $text-muted;
        margin: 0 0 0 1;
    }

    #main-area {
        width: 1fr;
        height: 100%;
        layout: vertical;
    }

    #chat-container {
        height: 1fr;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }

    #input-area {
        height: auto;
        padding: 0 1 1 1;
        layout: horizontal;
    }

    Input {
        width: 1fr;
        margin-right: 1;
    }

    Button {
        width: auto;
    }

    .message-block {
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

    .tool-panel {
        background: $panel;
        border: solid $success;
        padding: 1;
        margin: 1 0;
    }

    .streaming-indicator {
        color: $warning;
        text-style: italic;
    }

    .error-message {
        color: $error;
        background: $panel;
        border: solid $error;
        padding: 1;
        margin: 1 0;
    }
    """

    def __init__(self, config, agent_file: Path | None = None, session_id: str | None = None):
        super().__init__()
        self.config = config
        self.agent_file = agent_file
        self.session_id = session_id
        self.agent = None
        self.is_processing = False
        self.chat_text = Text("")
        self.streaming_text = ""  # Buffer for streaming content

    def compose(self):
        """Create child widgets."""
        yield Header()

        with Horizontal():
            # Sidebar
            with Vertical(id="sidebar"):
                yield Static("Agent Info", id="sidebar-title")
                with Vertical(id="agent-info"):
                    yield Label(f"Name: {self.agent_file.stem}")
                    yield Label("Model: Loading...")
                    yield Label("Provider: Loading...")

                with Vertical(id="tools-container"):
                    yield Label("Available Tools:", markup=True)
                    yield Static("Loading tools...", id="tools-list")

            # Main chat area
            with Vertical(id="main-area"):
                with ScrollableContainer(id="chat-container"):
                    yield Static(self.chat_text, id="chat-content")

                with Horizontal(id="input-area"):
                    yield Input(
                        placeholder="Type your message...",
                        id="user-input",
                        disabled=True
                    )
                    yield Button("Send", variant="primary", id="send-button", disabled=True)

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the agent when the screen is mounted."""
        self.load_agent()

    @work(exclusive=True, thread=True)
    def load_agent(self) -> None:
        """Load the agent from the markdown file or session in a background thread."""
        try:
            if self.session_id:
                # Load from session
                from vindao_agents import Agent
                self.agent = Agent.from_session_id(self.session_id)
                # Get agent name from session config
                if hasattr(self.agent.config, 'behavior'):
                    # Try to extract agent name from behavior or use model
                    agent_name = self.agent.config.model
                else:
                    agent_name = self.agent.config.model

                # Restore chat history
                self.app.call_from_thread(self.restore_chat_history)
            else:
                # Load from markdown file
                self.agent = Agent.from_markdown(str(self.agent_file))

            # Update UI from main thread
            self.app.call_from_thread(self.on_agent_loaded)
        except Exception as e:
            error_msg = f"Error loading agent: {str(e)}"
            self.app.call_from_thread(self.add_error_message, error_msg)

    def on_agent_loaded(self) -> None:
        """Called when agent is successfully loaded."""
        # Update agent info
        agent_info = self.query_one("#agent-info", Vertical)
        agent_info.remove_children()

        # Get agent name
        if self.agent_file:
            agent_name = self.agent_file.stem
        elif self.session_id:
            agent_name = f"Session ({self.agent.config.model})"
        else:
            agent_name = "Unknown"

        agent_info.mount(Label(f"Name: {agent_name}"))
        agent_info.mount(Label(f"Model: {self.agent.config.model}"))
        agent_info.mount(Label(f"Provider: {self.agent.config.provider}"))

        # Update tools list
        tools_list = self.query_one("#tools-list", Static)
        if self.agent.tools:
            tool_items = "\n".join([f"• {name}" for name in self.agent.tools.keys()])
            tools_list.update(tool_items)
        else:
            tools_list.update("No tools available")

        # Enable input
        self.query_one("#user-input", Input).disabled = False
        self.query_one("#send-button", Button).disabled = False

        # Add welcome message if not resuming session
        if not self.session_id:
            agent_name = self.agent_file.stem if self.agent_file else "Agent"
            self.add_system_message(f"Chat with {agent_name} started. Type your message below.")

    def restore_chat_history(self) -> None:
        """Restore chat history from loaded session."""
        if not self.agent or not self.agent.state.messages:
            return

        # Skip system message and rebuild chat display
        for message in self.agent.state.messages[1:]:  # Skip system message
            if isinstance(message, UserMessage):
                self.chat_text.append("\n\n")
                self.chat_text.append("You: ", style="bold cyan")
                self.chat_text.append(message.content)
            elif isinstance(message, AssistantMessage):
                self.chat_text.append("\n\n")
                self.chat_text.append("Agent: ", style="bold green")
                # Use markdown if available
                try:
                    md = Markdown(message.content)
                    self.chat_text.append(message.content)
                except:
                    self.chat_text.append(message.content)
            elif isinstance(message, ToolMessage):
                self.chat_text.append(f"\n\n[Tool: {message.name}]", style="bold magenta")
                self.chat_text.append("\n")
                output = message.content[:500]
                self.chat_text.append(output, style="dim")
                if len(message.content) > 500:
                    self.chat_text.append("\n... (output truncated)", style="dim italic")

        # Update display
        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.add_system_message("Session restored. Continue your conversation below.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button press."""
        if event.button.id == "send-button" and not self.is_processing:
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "user-input" and not self.is_processing:
            self.send_message()

    def send_message(self) -> None:
        """Send user message and get agent response."""
        input_widget = self.query_one("#user-input", Input)
        message = input_widget.value.strip()

        if not message or not self.agent:
            return

        # Clear input
        input_widget.value = ""

        # Disable input while processing
        self.is_processing = True
        input_widget.disabled = True
        self.query_one("#send-button", Button).disabled = True

        # Add user message to chat
        self.add_user_message(message)

        # Show streaming indicator
        self.add_streaming_indicator()

        # Process with agent in background
        self.process_agent_response(message)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the chat display."""
        self.chat_text.append("\n\n")
        self.chat_text.append("You: ", style="bold cyan")
        self.chat_text.append(content)

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def add_agent_message(self, content: str) -> None:
        """Add an agent message to the chat display."""
        # Remove streaming indicator if present
        text_str = str(self.chat_text)
        if "Agent is thinking" in text_str:
            # Reconstruct without the streaming indicator
            lines = text_str.split("\n")
            filtered = [l for l in lines if "Agent is thinking" not in l]
            self.chat_text = Text("\n".join(filtered))

        self.chat_text.append("\n\n")
        self.chat_text.append("Agent: ", style="bold green")
        self.chat_text.append(content)

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def add_tool_output(self, tool_name: str, output: str) -> None:
        """Add tool output to the chat display."""
        self.chat_text.append("\n\n")
        self.chat_text.append(f"[Tool: {tool_name}]", style="bold magenta")
        self.chat_text.append("\n")
        self.chat_text.append(output[:500], style="dim")  # Limit output length
        if len(output) > 500:
            self.chat_text.append("\n... (output truncated)", style="dim italic")

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def add_streaming_indicator(self) -> None:
        """Add a streaming/thinking indicator."""
        self.chat_text.append("\n\n")
        self.chat_text.append("Agent is thinking...", style="italic yellow")

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def add_system_message(self, content: str) -> None:
        """Add a system message to the chat display."""
        self.chat_text.append("\n")
        self.chat_text.append(content, style="dim italic")

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def scroll_to_bottom(self) -> None:
        """Scroll chat container to bottom."""
        container = self.query_one("#chat-container", ScrollableContainer)
        container.scroll_end(animate=False)

    @work(exclusive=True, thread=True)
    def process_agent_response(self, message: str) -> None:
        """Process agent response with real-time streaming in background thread."""
        if not self.agent:
            return

        accumulated_content = ""
        accumulated_reasoning = ""

        try:
            # Start with agent prefix
            self.app.call_from_thread(self.start_agent_response)

            for chunk, chunk_type in self.agent.instruct(message):
                if chunk_type == "reasoning":
                    accumulated_reasoning += chunk
                    # Optionally show reasoning progress
                    self.app.call_from_thread(self.update_reasoning_indicator, accumulated_reasoning)
                elif chunk_type == "content":
                    accumulated_content += chunk
                    # Stream content in real-time
                    self.app.call_from_thread(self.stream_agent_content, chunk)
                elif chunk_type == "tool":
                    # Tool execution - show it immediately
                    self.app.call_from_thread(self.add_tool_output, chunk.name, chunk.result)

        except Exception as e:
            error_msg = f"Error: {str(e)}\n\nStack trace:\n{type(e).__name__}: {str(e)}"
            self.app.call_from_thread(self.add_error_message, error_msg)
        finally:
            # Re-enable input
            self.app.call_from_thread(self.enable_input)

    def start_agent_response(self) -> None:
        """Start a new agent response section."""
        # Remove streaming indicator
        text_str = str(self.chat_text)
        if "Agent is thinking" in text_str:
            lines = text_str.split("\n")
            filtered = [l for l in lines if "Agent is thinking" not in l]
            self.chat_text = Text("\n".join(filtered))

        self.chat_text.append("\n\nAgent: ", style="bold green")
        self.streaming_text = ""

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def stream_agent_content(self, chunk: str) -> None:
        """Stream agent content chunk in real-time."""
        self.streaming_text += chunk

        # Simply append the chunk to the chat text
        self.chat_text.append(chunk)

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

    def update_reasoning_indicator(self, reasoning: str) -> None:
        """Update reasoning progress indicator (optional - can show thinking progress)."""
        # For now, just update the console log
        # Could add a subtle indicator in the UI
        pass

    def add_error_message(self, error: str) -> None:
        """Add an error message to the chat display."""
        self.chat_text.append("\n\n")
        self.chat_text.append("⚠ Error: ", style="bold red")
        self.chat_text.append(error, style="red")

        chat_content = self.query_one("#chat-content", Static)
        chat_content.update(self.chat_text)
        self.scroll_to_bottom()

        # Also show a notification
        self.notify("An error occurred", severity="error", timeout=5)

    def enable_input(self) -> None:
        """Re-enable input after processing."""
        self.is_processing = False
        self.query_one("#user-input", Input).disabled = False
        self.query_one("#send-button", Button).disabled = False
        self.query_one("#user-input", Input).focus()

    def action_go_back(self) -> None:
        """Go back to home screen."""
        self.app.pop_screen()

    def action_clear_chat(self) -> None:
        """Clear the chat history."""
        if self.agent:
            # Reset agent messages but keep system message
            self.agent.state.messages = self.agent._Agent__build_initial_messages()

            # Clear display
            self.chat_text = Text("")
            self.add_system_message(f"Chat cleared. Start a new conversation.")
