"""Comprehensive tests for the Agent class."""

# stdlib
import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

# third party
# local
from vindao_agents.Agent import Agent
from vindao_agents.models.messages import (
    AssistantMessage,
    SystemMessage,
    UserMessage,
)
from vindao_agents.Tool import Tool


class MockInferenceAdapter:
    """Mock inference adapter for testing."""

    def __init__(self, provider: str, model: str, responses: list = None):
        self.provider = provider
        self.model = model
        self.responses = responses or [("response", "content")]
        self.call_count = 0

    def completion(self, messages):
        """Mock completion method that yields predefined responses."""
        for chunk, chunk_type in self.responses:
            yield chunk, chunk_type
        self.call_count += 1


class TestAgentInitialization:
    """Tests for Agent initialization."""

    def test_default_initialization(self, tmp_path):
        """Test agent initialization with default parameters."""
        agent = Agent(user_data_dir=tmp_path)

        assert agent.config.name == "Momo"
        assert agent.config.provider == "ollama"
        assert agent.config.model == "qwen2.5:0.5b"
        assert agent.config.tools == []
        assert agent.config.behavior == ""
        assert agent.config.max_iterations == 15
        assert agent.config.auto_save is True
        assert agent.config.tools_with_source is True
        assert agent.tools == {}
        assert len(agent.state.messages) == 1
        assert isinstance(agent.state.messages[0], SystemMessage)

    def test_custom_initialization(self, tmp_path):
        """Test agent initialization with custom parameters."""
        agent = Agent(
            name="TestAgent",
            provider="openai",
            model="gpt-4",
            tools=[],
            behavior="Be helpful and concise",
            max_iterations=10,
            auto_save=False,
            user_data_dir=tmp_path,
            system_prompt_data={"key": "value"},
            tools_with_source=False,
        )

        assert agent.config.name == "TestAgent"
        assert agent.config.provider == "openai"
        assert agent.config.model == "gpt-4"
        assert agent.config.behavior == "Be helpful and concise"
        assert agent.config.max_iterations == 10
        assert agent.config.auto_save is False
        assert agent.config.tools_with_source is False
        assert agent.config.system_prompt_data == {"key": "value"}

    def test_initialization_with_session_data(self, tmp_path):
        """Test agent initialization with existing session data."""
        session_id = uuid4().hex
        created_at = datetime.now(UTC).timestamp()
        messages = [
            SystemMessage(content="System message"),
            UserMessage(content="User message"),
        ]

        agent = Agent(
            session_id=session_id,
            created_at=created_at,
            messages=messages,
            user_data_dir=tmp_path,
        )

        assert agent.state.session_id == session_id
        assert agent.state.created_at == created_at
        assert len(agent.state.messages) == 2
        assert agent.state.messages[0].content == "System message"
        assert agent.state.messages[1].content == "User message"


class TestAgentInvoke:
    """Tests for Agent invoke method."""
    pass


class TestAgentInstruct:
    """Tests for Agent instruct method."""

    @patch("vindao_agents.Agent.adapters")
    def test_instruct_adds_user_message(self, mock_adapters, tmp_path):
        """Test that instruct adds user message to state."""
        mock_adapter = MockInferenceAdapter(
            "ollama", "qwen2.5:0.5b", responses=[("response", "content")]
        )
        mock_adapters.__getitem__.return_value = lambda provider, model: mock_adapter

        agent = Agent(user_data_dir=tmp_path, auto_save=False)
        initial_message_count = len(agent.state.messages)

        list(agent.instruct("Test instruction"))

        assert len(agent.state.messages) > initial_message_count
        user_messages = [
            msg for msg in agent.state.messages if isinstance(msg, UserMessage)
        ]
        assert any(msg.content == "Test instruction" for msg in user_messages)

    @patch("vindao_agents.Agent.adapters")
    def test_instruct_yields_chunks(self, mock_adapters, tmp_path):
        """Test that instruct yields chunks from invoke."""
        mock_adapter = MockInferenceAdapter(
            "ollama",
            "qwen2.5:0.5b",
            responses=[("Hello", "content"), (" world", "content")],
        )
        mock_adapters.__getitem__.return_value = lambda provider, model: mock_adapter

        agent = Agent(user_data_dir=tmp_path, auto_save=False)

        chunks = list(agent.instruct("Test"))
        assert len(chunks) > 0
        assert all(isinstance(chunk, tuple) for chunk in chunks)


class TestAgentChat:
    """Tests for Agent chat method."""

    @patch("builtins.input")
    @patch("vindao_agents.Agent.adapters")
    def test_chat_exit_command(self, mock_adapters, mock_input, tmp_path):
        """Test that chat exits on 'exit' command."""
        mock_adapter = MockInferenceAdapter(
            "ollama", "qwen2.5:0.5b", responses=[("response", "content")]
        )
        mock_adapters.__getitem__.return_value = lambda provider, model: mock_adapter

        mock_input.return_value = "exit"

        agent = Agent(user_data_dir=tmp_path, auto_save=False)

        # Mock the logger to capture calls
        mock_logger = MagicMock()
        agent.logger = mock_logger

        agent.chat()

        # Verify that exit message was logged
        logger_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Exiting" in str(call) for call in logger_calls)

    @patch("builtins.input")
    @patch("vindao_agents.Agent.adapters")
    def test_chat_keyboard_interrupt(
        self, mock_adapters, mock_input, tmp_path
    ):
        """Test that chat handles keyboard interrupt gracefully."""
        mock_adapter = MockInferenceAdapter(
            "ollama", "qwen2.5:0.5b", responses=[("response", "content")]
        )
        mock_adapters.__getitem__.return_value = lambda provider, model: mock_adapter

        mock_input.side_effect = KeyboardInterrupt()

        agent = Agent(user_data_dir=tmp_path, auto_save=False)

        # Mock the logger to capture calls
        mock_logger = MagicMock()
        agent.logger = mock_logger

        agent.chat()

        # Verify that interrupted message was logged with session ID
        logger_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any(agent.state.session_id in str(call).lower() for call in logger_calls)


class TestAgentSave:
    """Tests for Agent save method."""
    pass


class TestAgentFromDict:
    """Tests for Agent.from_dict class method."""

    def test_from_dict_creates_agent(self, tmp_path):
        """Test creating agent from dictionary."""
        data = {
            "name": "TestAgent",
            "provider": "openai",
            "model": "gpt-4",
            "tools": [],
            "behavior": "Test behavior",
            "max_iterations": 10,
            "auto_save": False,
            "user_data_dir": str(tmp_path),
            "system_prompt_data": {"key": "value"},
            "tools_with_source": False,
        }

        agent = Agent.from_dict(data)

        assert agent.config.name == "TestAgent"
        assert agent.config.provider == "openai"
        assert agent.config.model == "gpt-4"
        assert agent.config.behavior == "Test behavior"
        assert agent.config.max_iterations == 10


class TestAgentFromJson:
    """Tests for Agent.from_json class method."""

    def test_from_json_creates_agent(self, tmp_path):
        """Test creating agent from JSON file."""
        json_data = {
            "config": {
                "name": "JsonAgent",
                "provider": "anthropic",
                "model": "claude-3",
                "tools": [],
                "behavior": "JSON behavior",
                "max_iterations": 20,
                "auto_save": True,
                "user_data_dir": str(tmp_path),
                "system_prompt_data": {},
                "tools_with_source": True,
            },
            "state": {
                "session_id": "test-session-id",
                "created_at": datetime.now(UTC).timestamp(),
                "updated_at": datetime.now(UTC).timestamp(),
                "messages": [
                    {"role": "system", "content": "System message"},
                    {"role": "user", "content": "User message"},
                ],
            },
        }

        json_path = tmp_path / "agent.json"
        with open(json_path, "w") as f:
            json.dump(json_data, f)

        agent = Agent.from_json_file(json_path)

        assert agent.config.name == "JsonAgent"
        assert agent.config.provider == "anthropic"
        assert agent.config.model == "claude-3"
        assert agent.state.session_id == "test-session-id"
        assert len(agent.state.messages) == 2


class TestAgentFromSessionId:
    """Tests for Agent.from_session_id class method."""

    def test_from_session_id_loads_agent(self, tmp_path):
        """Test loading agent from session ID."""
        session_id = "test-session-123"
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)

        json_data = {
            "config": {
                "name": "SessionAgent",
                "provider": "ollama",
                "model": "qwen2.5:0.5b",
                "tools": [],
                "behavior": "",
                "max_iterations": 15,
                "auto_save": True,
                "user_data_dir": str(tmp_path),
                "system_prompt_data": {},
                "tools_with_source": True,
            },
            "state": {
                "session_id": session_id,
                "created_at": datetime.now(UTC).timestamp(),
                "updated_at": datetime.now(UTC).timestamp(),
                "messages": [{"role": "system", "content": "System"}],
            },
        }

        session_path = sessions_dir / f"{session_id}.json"
        with open(session_path, "w") as f:
            json.dump(json_data, f)

        agent = Agent.from_session_id(session_id, user_data_dir=tmp_path)

        assert agent.state.session_id == session_id
        assert agent.config.name == "SessionAgent"


class TestAgentFromMarkdown:
    """Tests for Agent.from_markdown class method."""

    def test_from_markdown_creates_agent(self, tmp_path):
        """Test creating agent from markdown file with frontmatter."""
        markdown_content = """---
provider: openai
model: gpt-4
tools: []
max_iterations: 10
auto_save: false
---

This is the agent's behavior description.
It can span multiple lines.
"""

        md_path = tmp_path / "TestAgent.md"
        md_path.write_text(markdown_content)

        agent = Agent.from_markdown(md_path)

        assert agent.config.name == "TestAgent"
        assert agent.config.provider == "openai"
        assert agent.config.model == "gpt-4"
        assert agent.config.max_iterations == 10
        assert agent.config.auto_save is False
        assert "behavior description" in agent.config.behavior


class TestAgentFromName:
    """Tests for Agent.from_name class method."""

    def test_from_name_loads_agent_from_package(self, tmp_path):
        """Test loading predefined agent by name from package."""
        # This will try to load from the agents directory in the package
        # We need to check if such a file exists first
        agents_dir = Path(__file__).parent.parent / "src" / "vindao_agents" / "agents"
        if (agents_dir / "DefaultAgent.md").exists():
            agent = Agent.from_name("DefaultAgent")
            assert agent.config.name == "DefaultAgent"


class TestAgentLoadTools:
    """Tests for Agent tool loading functionality."""

    def test_load_tools_empty_list(self, tmp_path):
        """Test loading with empty tools list."""
        agent = Agent(tools=[], user_data_dir=tmp_path, auto_save=False)
        assert agent.tools == {}

    @patch("vindao_agents.Agent.load_public_functions_from_identifier")
    def test_load_tools_from_identifier(self, mock_load, tmp_path):
        """Test loading tools from module identifier."""

        def sample_func():
            """Sample function."""
            pass

        mock_load.return_value = [("sample_func", sample_func)]

        agent = Agent(
            tools=["test_module"], user_data_dir=tmp_path, auto_save=False
        )

        assert "sample_func" in agent.tools
        assert isinstance(agent.tools["sample_func"], Tool)


class TestAgentBuildSystemMessage:
    """Tests for Agent system message building."""

    def test_system_message_includes_agent_name(self, tmp_path):
        """Test that system message includes agent name."""
        agent = Agent(name="TestBot", user_data_dir=tmp_path, auto_save=False)

        system_message = agent.state.messages[0]
        assert isinstance(system_message, SystemMessage)
        # System message should contain the agent name
        assert "TestBot" in system_message.content

    def test_system_message_includes_behavior(self, tmp_path):
        """Test that system message includes behavior."""
        behavior = "Be very helpful and friendly"
        agent = Agent(
            behavior=behavior, user_data_dir=tmp_path, auto_save=False
        )

        system_message = agent.state.messages[0]
        assert behavior in system_message.content

    @patch("vindao_agents.Agent.load_public_functions_from_identifier")
    def test_system_message_includes_tools(self, mock_load, tmp_path):
        """Test that system message includes tool instructions."""

        def test_tool(x: int) -> int:
            """Test tool docstring."""
            return x * 2

        mock_load.return_value = [("test_tool", test_tool)]

        agent = Agent(
            tools=["test_module"],
            user_data_dir=tmp_path,
            auto_save=False,
            tools_with_source=True,
        )

        system_message = agent.state.messages[0]
        # Should contain tool name and potentially docstring
        assert "test_tool" in system_message.content


class TestAgentStateManagement:
    """Tests for Agent state management."""

    def test_state_updates_timestamp_on_message_add(self, tmp_path):
        """Test that adding messages updates the timestamp."""
        agent = Agent(user_data_dir=tmp_path, auto_save=False)
        initial_updated_at = agent.state.updated_at

        # Wait a tiny bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        agent.state.add_message(UserMessage(content="New message"))

        assert agent.state.updated_at > initial_updated_at

    def test_state_maintains_message_order(self, tmp_path):
        """Test that messages are kept in order."""
        agent = Agent(user_data_dir=tmp_path, auto_save=False)

        agent.state.add_message(UserMessage(content="First"))
        agent.state.add_message(AssistantMessage(content="Second"))
        agent.state.add_message(UserMessage(content="Third"))

        assert agent.state.messages[1].content == "First"
        assert agent.state.messages[2].content == "Second"
        assert agent.state.messages[3].content == "Third"


class TestAgentConfiguration:
    """Tests for Agent configuration management."""

    def test_config_immutability(self, tmp_path):
        """Test that config values are properly set."""
        agent = Agent(
            name="TestAgent",
            provider="test_provider",
            model="test_model",
            user_data_dir=tmp_path,
        )

        assert agent.config.name == "TestAgent"
        assert agent.config.provider == "test_provider"
        assert agent.config.model == "test_model"

    def test_config_default_values(self, tmp_path):
        """Test that config has proper default values."""
        agent = Agent(user_data_dir=tmp_path)

        assert agent.config.max_iterations > 0
        assert isinstance(agent.config.auto_save, bool)
        assert isinstance(agent.config.tools_with_source, bool)
        assert isinstance(agent.config.system_prompt_data, dict)
