"""Agent orchestrator for managing AI agent interactions and tool execution."""

# stdlib
import json
from datetime import UTC, datetime
from os import getenv
from pathlib import Path
from uuid import uuid4 as uuid

from dotenv import load_dotenv

from vindao_agents.AgentStores import AgentStore, JsonAgentStore, stores
from vindao_agents.builders import MessageBuilder
from vindao_agents.executors import execute_tool_call
from vindao_agents.formatters import ConsoleFormatter
from vindao_agents.InferenceAdapters import InferenceAdapter, LiteLLMInferenceAdapter, adapters
from vindao_agents.loaders import (
    load_agent_from_markdown,
    load_messages_from_dicts,
    load_public_functions_from_identifier,
)

# local
from vindao_agents.models.messages import AssistantMessage, MessageType, ToolMessage, UserMessage
from vindao_agents.models.tool import ToolCall
from vindao_agents.Tool import Tool
from vindao_agents.ToolParsers import AtSyntaxParser, ToolParser, parsers
from vindao_agents.utils import AgentLogger, get_default_logger, resolve_path

from .models.agent import AgentConfig, AgentState

load_dotenv()


class Agent:
    tools: dict[str, Tool]
    config: AgentConfig
    state: AgentState
    inference_adapter: InferenceAdapter
    store: AgentStore
    parser: ToolParser
    logger: AgentLogger

    def __init__(
        self,
        name: str = "Momo",
        provider: str = "ollama",
        model: str = "qwen2.5:0.5b",
        tools: list[str] = [],
        behavior: str = "",
        max_iterations: int = 15,
        auto_save: bool = True,
        user_data_dir: str | Path = getenv("USER_DATA_DIR", Path.cwd() / ".vindao_agents"),
        system_prompt_data: dict | None = None,
        tools_with_source: bool = True,
        session_id: str = uuid().hex,
        created_at: float = datetime.now(UTC).timestamp(),
        updated_at: float = datetime.now(UTC).timestamp(),
        messages: list[MessageType] | None = None,
        inference_adapter: InferenceAdapter | type[InferenceAdapter] | str = LiteLLMInferenceAdapter,
        store: AgentStore | type[AgentStore] | str = JsonAgentStore,
        parser: ToolParser | type[ToolParser] | str = AtSyntaxParser,
        logger: AgentLogger | None = None,
    ):
        self.config = AgentConfig(
            name=name,
            provider=provider,
            model=model,
            tools=tools,
            behavior=behavior,
            max_iterations=max_iterations,
            auto_save=auto_save,
            user_data_dir=str(user_data_dir),
            system_prompt_data=system_prompt_data or {},
            tools_with_source=tools_with_source,
            inference_adapter=inference_adapter if isinstance(inference_adapter, str) else "litellm",
            parser=parser if isinstance(parser, str) else "at_syntax",
        )

        # Initialize logger
        self.logger = logger if logger is not None else get_default_logger()

        self.tools = self.__load_tools(tools)
        if isinstance(parser, str):
            parser_cls: type[ToolParser] = parsers.get(parser, AtSyntaxParser)
            self.parser = parser_cls()
        elif isinstance(parser, type):
            self.parser = parser()
        else:
            self.parser = parser
        if not messages:
            message_builder = MessageBuilder()
            system_message = message_builder.build_system_message(
                model=self.config.model, tools=self.tools, parser=self.parser, config=self.config
            )
            messages = [system_message]
        self.state = AgentState(session_id=session_id, created_at=created_at, updated_at=updated_at, messages=messages)
        if isinstance(inference_adapter, str):
            adapter_cls: type[InferenceAdapter] = adapters.get(inference_adapter, LiteLLMInferenceAdapter)
            self.inference_adapter = adapter_cls(provider=self.config.provider, model=self.config.model)
        # If inference_adapter is a class, instantiate it; if it's already an instance, use it directly
        elif isinstance(inference_adapter, type):
            self.inference_adapter = inference_adapter(provider=self.config.provider, model=self.config.model)
        else:
            self.inference_adapter = inference_adapter

        if isinstance(store, str):
            store_cls: type[AgentStore] = stores.get(store, JsonAgentStore)
            self.store = store_cls()
        elif isinstance(store, type):
            self.store = store()
        else:
            self.store = store

    def invoke(self, iteration: int = 0, max_iterations: int | None = None):
        """Invoke the agent's reasoning and tool usage process."""
        if max_iterations is None:
            max_iterations = self.config.max_iterations
        accumulated_reasoning = ""
        accumulated_content = ""
        tool_call_enabled = True

        if iteration == max_iterations - 1:
            self.state.add_message(
                UserMessage(
                    content="You have reached the maximum number of iterations. Please provide a summary without further tool usage."
                )
            )
            tool_call_enabled = False

        for chunk, chunk_type in self.inference_adapter.complete_chat(self.state.messages):
            if chunk_type == "reasoning":
                accumulated_reasoning += chunk

            elif chunk_type == "content":
                accumulated_content += chunk
            yield chunk, chunk_type
            if accumulated_content.startswith("@DISABLE_TOOL_CALL@"):
                tool_call_enabled = False
            if tool_call_enabled:
                call = self.parser.parse(accumulated_content, list(self.tools.keys()))
                if call:
                    tool_name, tool_call_str = call
                    result = str(execute_tool_call(tool_call_str, self.tools[tool_name]))
                    tool_call_obj = ToolCall(name=tool_name, call=tool_call_str, result=result)
                    yield tool_call_obj, "tool"
                    self.state.add_message(
                        AssistantMessage(
                            content=accumulated_content,
                            reasoning_content=accumulated_reasoning.strip(),
                            tool_call=tool_call_obj,
                        )
                    )
                    self.state.add_message(
                        ToolMessage(content=tool_call_obj.result, name=tool_call_obj.name, tool_call=tool_call_obj)
                    )
                    return (yield from self.invoke(iteration + 1, max_iterations=max_iterations))

        if accumulated_content.startswith("@DISABLE_TOOL_CALL@"):
            accumulated_content = accumulated_content.replace("@DISABLE_TOOL_CALL@", "", 1).lstrip()
        self.state.add_message(AssistantMessage(content=accumulated_content, reasoning_content=accumulated_reasoning))
        if self.config.auto_save:
            self.store.save(self)

    def instruct(self, instruction: str):
        self.state.add_message(UserMessage(content=instruction))
        for chunk, chunk_type in self.invoke():
            yield chunk, chunk_type

    def chat(self):
        """Start an interactive chat session with the agent."""
        formatter = ConsoleFormatter(self.logger)
        formatter.display_message("Starting chat session with the agent. Type 'exit' to quit.")
        formatter.display_message(f"Session ID: {self.state.session_id}")
        try:
            while True:
                user_input = input("\n\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    formatter.display_message(f"Exiting chat session.\nSession ID: {self.state.session_id}")
                    break
                for chunk, chunk_type in self.instruct(user_input):
                    formatter.display_event(chunk, chunk_type)
                formatter.display_newline()
        except KeyboardInterrupt:
            formatter.display_message(f"Exiting chat session.\nSession ID: {self.state.session_id}")

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """Create an Agent instance from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json_string(cls, json_str: str) -> "Agent":
        """Create an Agent instance from a JSON string."""
        data = json.loads(json_str)
        config_data = data.get("config", {})
        state_data = data.get("state", {})
        messages = load_messages_from_dicts(state_data.get("messages", []))
        combined_data = {**config_data, **state_data, "messages": messages}
        return cls.from_dict(combined_data)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "Agent":
        """Create an Agent instance from a JSON file."""
        data = Path(path).read_text()
        return cls.from_json_string(data)

    @classmethod
    def from_session_id(cls, session_id: str, user_data_dir: str | Path | None = None) -> "Agent":
        """Create an Agent instance from a session ID by loading the corresponding saved state."""
        base_path_str = user_data_dir or getenv("USER_DATA_DIR") or str(Path.cwd() / ".vindao_agents")
        base_path = Path(base_path_str)
        session_path = base_path / "sessions" / f"{session_id}.json"
        return cls.from_json_file(session_path)

    @classmethod
    def from_markdown(cls, path: str | Path) -> "Agent":
        """Create an Agent instance from a markdown file with frontmatter."""
        return cls(**load_agent_from_markdown(path))

    @classmethod
    def from_name(cls, name: str) -> "Agent":
        """Create an Agent instance from a predefined agent name."""
        search_dirs: list[str | Path] = [Path.cwd() / "agents", Path(__file__).parent / "agents"]
        agent_path = resolve_path(f"{name}.md", search_dirs)
        return cls.from_markdown(agent_path)

    def __load_tools(self, tool_identifiers: list[str]) -> dict[str, Tool]:
        loaded_tools = {}
        for tool in tool_identifiers:
            loaded_functions = load_public_functions_from_identifier(tool)
            for name, f in loaded_functions:
                loaded_tools[name] = Tool(f)

        return loaded_tools
