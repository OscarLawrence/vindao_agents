"""Agent orchestrator for managing AI agent interactions and tool execution."""
# stdlib
from uuid import uuid4 as uuid
from datetime import datetime, timezone
from pathlib import Path
from os import getenv
from dotenv import load_dotenv
import json

# local
from vindao_agents.models.messages import MessageType, SystemMessage, UserMessage, AssistantMessage, ToolMessage
from vindao_agents.models.tool import ToolCall
from .models.agent import AgentConfig, AgentState
from vindao_agents.Tool import Tool
from vindao_agents.loaders import load_public_functions_from_identifier, load_system_message_template, load_messages_from_dicts, load_agent_from_markdown
from vindao_agents.formatters import format_prompt
from vindao_agents.ToolParsers import parsers, ToolParser, AtSyntaxParser
from vindao_agents.executors import execute_tool_call
from vindao_agents.InferenceAdapters import adapters, InferenceAdapter, LiteLLMInferenceAdapter
from vindao_agents.AgentStores import stores, JsonAgentStore, AgentStore

load_dotenv()

class Agent:

    tools: dict[str, Tool]
    config: AgentConfig
    state: AgentState
    inference_adapter: InferenceAdapter
    store: AgentStore
    parser: ToolParser

    def __init__(
            self,
            name: str = 'Momo',
            provider: str = 'ollama',
            model: str = 'qwen2.5:0.5b',
            tools: list[str] = [],
            behavior: str = "",
            max_iterations: int = 15,
            auto_save: bool = True,
            user_data_dir: str | Path = getenv("USER_DATA_DIR", Path.cwd() / ".vindao_agents"),
            system_prompt_data: dict | None = None,
            tools_with_source: bool = True,
            session_id: str = uuid().hex,
            created_at: float = datetime.now(timezone.utc).timestamp(),
            updated_at: float = datetime.now(timezone.utc).timestamp(),
            messages: list[MessageType] | None = None,
            inference_adapter: InferenceAdapter | str = LiteLLMInferenceAdapter,
            store: AgentStore | str = JsonAgentStore,
            parser: ToolParser | str = AtSyntaxParser,
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

        # Initialize parser early since it's needed for building the system message
        if isinstance(parser, str):
            parser = parsers.get(parser, AtSyntaxParser)
        self.parser = parser()

        self.tools = self.__load_tools(tools)
        if not messages:
            messages = [self.__build_system_message()]
        self.state = AgentState(
            session_id=session_id,
            created_at=created_at,
            updated_at=updated_at,
            messages=messages
        )
        if isinstance(inference_adapter, str):
            inference_adapter = adapters.get(inference_adapter, LiteLLMInferenceAdapter)
        self.inference_adapter = inference_adapter(provider=self.config.provider, model=self.config.model)

        if isinstance(store, str):
            store = stores.get(store, JsonAgentStore)
        self.store = store()

    def invoke(self, iteration: int = 0, max_iterations: int | None = None):
        """Invoke the agent's reasoning and tool usage process."""
        if max_iterations is None:
            max_iterations = self.config.max_iterations
        accumulated_reasoning = ""
        accumulated = ""
        tool_call_enabled = True

        if iteration == max_iterations - 1:
            self.state.add_message(UserMessage(content="You have reached the maximum number of iterations. Please provide a summary without further tool usage."))
            tool_call_enabled = False

        for chunk, chunk_type in self.inference_adapter.complete_chat(self.state.messages):

            if chunk_type == "reasoning":
                accumulated_reasoning += chunk
                
            elif chunk_type == "content":
                accumulated += chunk
            yield chunk, chunk_type
            if accumulated.startswith('@DISABLE_TOOL_CALL@'):
                tool_call_enabled = False
            if tool_call_enabled:
                call = self.parser.parse(accumulated, list(self.tools.keys()))
                if call:
                    tool_name, tool_call = call
                    result = str(execute_tool_call(tool_call, self.tools[tool_name]))
                    tool_call = ToolCall(
                        name=tool_name,
                        call=tool_call,
                        result=result
                    )
                    yield tool_call, 'tool'
                    self.state.add_message(AssistantMessage(
                        content=accumulated,
                        reasoning_content=accumulated_reasoning.strip(),
                        tool_call=tool_call
                    ))
                    self.state.add_message(ToolMessage(
                        content=tool_call.result,
                        name=tool_call.name,
                        tool_call=tool_call
                    ))
                    return (yield from self.invoke(iteration + 1, max_iterations=max_iterations))

        if accumulated.startswith('@DISABLE_TOOL_CALL@'):
            accumulated = accumulated.replace('@DISABLE_TOOL_CALL@', '', 1).lstrip()
        self.state.add_message(AssistantMessage(content=accumulated, reasoning_content=accumulated_reasoning))
        if self.config.auto_save:
            self.store.save(self)
        
    def instruct(self, instruction: str):
        self.state.add_message(UserMessage(content=instruction))
        for chunk, chunk_type in self.invoke():
            if chunk_type in ["content", "reasoning"]:
                print(chunk, end='', flush=True)
            elif chunk_type == "tool":
                print(f" =>\n{chunk.result}\n")
            yield chunk, chunk_type

    def chat(self):
        """Start an interactive chat session with the agent."""
        print("Starting chat session with the agent. Type 'exit' to quit.")
        print("Session ID:", self.state.session_id)
        try:
            while True:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']:
                    print(f"Exiting chat session.\nSession ID: {self.state.session_id}")
                    break
                for _ in self.instruct(user_input):
                    pass
                print("\n")  # Newline after agent response
        except KeyboardInterrupt:
            print(f"Exiting chat session.\nSession ID: {self.state.session_id}")


    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """Create an Agent instance from a dictionary."""
        return cls(
            **data
        )

    @classmethod
    def from_json_string(cls, data: str) -> "Agent":
        """Create an Agent instance from a JSON string."""
        data = json.loads(data)
        config_data = data.get("config", {})
        state_data = data.get("state", {})
        messages = load_messages_from_dicts(state_data.get("messages", []))
        data = {
            **config_data,
            **state_data,
            "messages": messages
        }
        return cls.from_dict(data)
    
    @classmethod
    def from_json_file(cls, path: str | Path) -> "Agent":
        """Create an Agent instance from a JSON file."""
        data = Path(path).read_text()
        return cls.from_json_string(data)

    @classmethod
    def from_session_id(cls, session_id: str, user_data_dir: str | Path | None = None) -> "Agent":
        """Create an Agent instance from a session ID by loading the corresponding saved state."""
        base_path = Path(user_data_dir or getenv("USER_DATA_DIR", Path.cwd() / ".vindao_agents"))
        session_path = base_path / "sessions" / f"{session_id}.json"
        return cls.from_json_file(session_path)

    @classmethod
    def from_markdown(cls, path: str | Path) -> "Agent":
        """Create an Agent instance from a markdown file with frontmatter."""
        return cls(**load_agent_from_markdown(path))
    
    @classmethod
    def from_name(cls, name: str) -> "Agent":
        """Create an Agent instance from a predefined agent name."""
        base_path = Path.cwd() / "agents"
        agent_path = base_path / f"{name}.md"
        if not agent_path.exists():
            agent_path = Path(__file__).parent / "agents" / f"{name}.md"
        return cls.from_markdown(agent_path)

    def __load_tools(self, tool_identifiers: list[str]) -> dict[str, Tool]:
        loaded_tools = {}
        for tool in tool_identifiers:
            loaded_functions = load_public_functions_from_identifier(tool)
            for name, f in loaded_functions:
                loaded_tools[name] = Tool(f)
            
        return loaded_tools
    
    def __build_system_message(self) -> SystemMessage:
        template = load_system_message_template(self.config.model, self.config.user_data_dir)
        tool_str = ""
        for tool in self.tools.values():
            tool_str += tool.to_instruction(include_source=self.config.tools_with_source)
        parser_instructions = self.parser.get_instructions()
        content = format_prompt(template, {**self.config.system_prompt_data, "model": self.config.model, "behavior": self.config.behavior, "name": self.config.name, "tools": tool_str.strip(), "parser_instructions": parser_instructions})
        return SystemMessage(content=content)

    
