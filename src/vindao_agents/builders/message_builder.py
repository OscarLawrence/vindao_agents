"""Message builder for constructing system messages from templates and configuration."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vindao_agents.models.agent import AgentConfig
    from vindao_agents.Tool import Tool
    from vindao_agents.ToolParsers import ToolParser

from vindao_agents.formatters import format_prompt
from vindao_agents.loaders import load_system_message_template
from vindao_agents.models.messages import SystemMessage


class MessageBuilder:
    """Builds system messages from templates and configuration.

    This class handles the construction of system messages by:
    - Loading appropriate templates based on model
    - Serializing tools into instruction format
    - Including parser-specific instructions
    - Formatting the final prompt with all configuration data

    This separation allows for easier testing and modification of
    message construction without modifying the Agent class.
    """

    def build_system_message(
        self,
        model: str,
        tools: dict[str, Tool],
        parser: ToolParser,
        config: AgentConfig
    ) -> SystemMessage:
        """Build a system message from configuration and components.

        Args:
            model: The model identifier for template selection
            tools: Dictionary mapping tool names to Tool instances
            parser: Tool parser instance for generating parser instructions
            config: Agent configuration containing behavior, name, and prompt data

        Returns:
            SystemMessage with formatted content ready for the agent
        """
        # Load the appropriate template for this model
        template = load_system_message_template(model, config.user_data_dir)

        # Serialize all tools into instruction format
        tool_str = self._serialize_tools(tools, config.tools_with_source)

        # Get parser-specific instructions
        parser_instructions = parser.get_instructions()

        # Format the final prompt with all data
        content = format_prompt(template, {
            **config.system_prompt_data,
            "model": model,
            "behavior": config.behavior,
            "name": config.name,
            "tools": tool_str,
            "parser_instructions": parser_instructions
        })

        return SystemMessage(content=content)

    def _serialize_tools(self, tools: dict[str, Tool], include_source: bool) -> str:
        """Serialize tools into instruction format.

        Args:
            tools: Dictionary mapping tool names to Tool instances
            include_source: Whether to include source code in tool instructions

        Returns:
            Formatted string containing all tool instructions
        """
        tool_str = ""
        for tool in tools.values():
            tool_str += tool.to_instruction(include_source=include_source)
        return tool_str.strip()
