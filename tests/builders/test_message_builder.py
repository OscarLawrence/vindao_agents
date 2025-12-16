"""Tests for MessageBuilder."""
from unittest.mock import Mock, patch

import pytest

from vindao_agents.builders import MessageBuilder
from vindao_agents.models.agent import AgentConfig
from vindao_agents.models.messages import SystemMessage
from vindao_agents.Tool import Tool


class TestMessageBuilder:
    """Test suite for MessageBuilder class."""

    @pytest.fixture
    def sample_tool(self):
        """Create a sample tool for testing."""
        def example_function(arg: str) -> str:
            """Example function for testing."""
            return f"Result: {arg}"
        return Tool(example_function)

    @pytest.fixture
    def mock_parser(self):
        """Create a mock parser for testing."""
        parser = Mock()
        parser.get_instructions = Mock(return_value="Use @function_name(arg='value') syntax")
        return parser

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        return AgentConfig(
            name="TestAgent",
            provider="ollama",
            model="test-model",
            tools=[],
            behavior="Be helpful and concise",
            max_iterations=10,
            auto_save=False,
            user_data_dir="/tmp/test",
            system_prompt_data={"custom_key": "custom_value"},
            tools_with_source=False,
            inference_adapter="litellm",
            parser="at_syntax"
        )

    @pytest.fixture
    def message_builder(self):
        """Create a MessageBuilder instance."""
        return MessageBuilder()

    def test_build_system_message_returns_system_message(
        self, message_builder, mock_parser, mock_config, sample_tool
    ):
        """Test that build_system_message returns a SystemMessage instance."""
        tools = {"example_function": sample_tool}

        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Test template: {{ name }}, {{ behavior }}, {{ tools }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools=tools,
                parser=mock_parser,
                config=mock_config
            )

            assert isinstance(result, SystemMessage)
            assert result.content is not None

    def test_build_system_message_includes_agent_name(
        self, message_builder, mock_parser, mock_config, sample_tool
    ):
        """Test that the system message includes the agent name."""
        tools = {"example_function": sample_tool}

        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Agent name: {{ name }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools=tools,
                parser=mock_parser,
                config=mock_config
            )

            assert "TestAgent" in result.content

    def test_build_system_message_includes_behavior(
        self, message_builder, mock_parser, mock_config, sample_tool
    ):
        """Test that the system message includes the behavior."""
        tools = {"example_function": sample_tool}

        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Behavior: {{ behavior }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools=tools,
                parser=mock_parser,
                config=mock_config
            )

            assert "Be helpful and concise" in result.content

    def test_build_system_message_includes_parser_instructions(
        self, message_builder, mock_parser, mock_config
    ):
        """Test that the system message includes parser instructions."""
        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Parser: {{ parser_instructions }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools={},
                parser=mock_parser,
                config=mock_config
            )

            assert "Use @function_name(arg='value') syntax" in result.content
            mock_parser.get_instructions.assert_called_once()

    def test_build_system_message_loads_correct_template(
        self, message_builder, mock_parser, mock_config
    ):
        """Test that the correct template is loaded based on model."""
        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Template content"

            message_builder.build_system_message(
                model="gpt-4",
                tools={},
                parser=mock_parser,
                config=mock_config
            )

            mock_load.assert_called_once_with("gpt-4", mock_config.user_data_dir)

    def test_serialize_tools_with_empty_tools(self, message_builder):
        """Test serializing an empty tools dictionary."""
        result = message_builder._serialize_tools({}, include_source=False)
        assert result == ""

    def test_serialize_tools_with_single_tool(self, message_builder, sample_tool):
        """Test serializing a single tool."""
        tools = {"example_function": sample_tool}

        result = message_builder._serialize_tools(tools, include_source=False)

        assert "example_function" in result
        assert len(result) > 0

    def test_serialize_tools_with_multiple_tools(self, message_builder):
        """Test serializing multiple tools."""
        def tool1():
            """First tool."""
            pass

        def tool2():
            """Second tool."""
            pass

        tools = {
            "tool1": Tool(tool1),
            "tool2": Tool(tool2)
        }

        result = message_builder._serialize_tools(tools, include_source=False)

        assert "tool1" in result
        assert "tool2" in result

    def test_serialize_tools_strips_whitespace(self, message_builder, sample_tool):
        """Test that serialized tools have whitespace stripped."""
        tools = {"example_function": sample_tool}

        result = message_builder._serialize_tools(tools, include_source=False)

        # Result should not start or end with whitespace
        assert result == result.strip()

    def test_serialize_tools_respects_include_source_flag(self, message_builder):
        """Test that include_source flag is passed to tool.to_instruction()."""
        mock_tool = Mock()
        mock_tool.to_instruction = Mock(return_value="Tool instruction\n")

        tools = {"mock_tool": mock_tool}

        # Test with include_source=True
        message_builder._serialize_tools(tools, include_source=True)
        mock_tool.to_instruction.assert_called_with(include_source=True)

        # Test with include_source=False
        message_builder._serialize_tools(tools, include_source=False)
        mock_tool.to_instruction.assert_called_with(include_source=False)

    def test_build_system_message_includes_custom_prompt_data(
        self, message_builder, mock_parser, mock_config
    ):
        """Test that custom system prompt data is included."""
        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Custom: {{ custom_key }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools={},
                parser=mock_parser,
                config=mock_config
            )

            assert "custom_value" in result.content

    def test_build_system_message_includes_model_in_prompt_data(
        self, message_builder, mock_parser, mock_config
    ):
        """Test that model is included in the prompt data."""
        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Model: {{ model }}"

            result = message_builder.build_system_message(
                model="special-model",
                tools={},
                parser=mock_parser,
                config=mock_config
            )

            assert "special-model" in result.content

    def test_build_system_message_with_tools_and_source(
        self, message_builder, mock_parser, sample_tool
    ):
        """Test building system message with tools_with_source=True."""
        config = AgentConfig(
            name="TestAgent",
            provider="ollama",
            model="test-model",
            tools=[],
            behavior="",
            max_iterations=10,
            auto_save=False,
            user_data_dir="/tmp/test",
            system_prompt_data={},
            tools_with_source=True,  # Enable source code
            inference_adapter="litellm",
            parser="at_syntax"
        )

        tools = {"example_function": sample_tool}

        with patch('vindao_agents.builders.message_builder.load_system_message_template') as mock_load:
            mock_load.return_value = "Tools: {{ tools }}"

            result = message_builder.build_system_message(
                model="test-model",
                tools=tools,
                parser=mock_parser,
                config=config
            )

            # When tools_with_source=True, the tool instruction should include more detail
            assert len(result.content) > len("Tools: ")
