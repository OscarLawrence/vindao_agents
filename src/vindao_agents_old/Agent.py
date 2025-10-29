# standard library imports
from typing import Callable
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4 as uuid
import json

# third-party imports
from prompt_toolkit import prompt
from rich import panel, print

# local imports
from .models.messages import Message, SystemMessage, UserMessage, AssistantMessage, ToolMessage
from .models.agent import AgentConfig, AgentState
from .models.tool import ToolCall
from .Tool import Tool
from .loaders import load_public_functions_from_identifier
from .parsers import parse_markdown, parse_tool_call
from .execution import execute_tool_call
from .LiteLLMAdapter import LiteLLMAdapter
from .cli import CLI

class Agent:

    provider: str
    model: str
    tools: dict[str, Tool]
    behavior: str
    max_iterations: int 

    session_id: str
    created_at: float
    updated_at: float
    messages: list[Message] | None
    
    def __init__(self,
            provider: str = 'openai',
            model: str = 'gpt-4.1-nano',
            tools: list[Callable | str] = [],
            behavior: str = "",
            max_iterations: int = 15,
            auto_save: bool = True,
            session_id: str = uuid().hex,
            created_at: float = datetime.now(timezone.utc).timestamp(),
            updated_at: float = datetime.now(timezone.utc).timestamp(),
            messages: list[Message] | None = None
        ):
        self.config = AgentConfig(
            provider=provider,
            model=model,
            tools=tools,
            behavior=behavior,
            max_iterations=max_iterations,
            auto_save=auto_save
        )
        self.tools = self.__load_tools(tools)

        self.state = AgentState(
            session_id=session_id,
            created_at=created_at,
            updated_at=updated_at,
            messages=messages or self.__build_initial_messages()
        )
        self.adapter = LiteLLMAdapter(provider, model)


    def invoke(self, iteration: int = 0):
        """Invoke the agent's reasoning and tool usage process."""
        accumulated_reasoning = ""
        accumulated = ""
        for chunk, chunk_type in self.adapter.completion(self.state.messages, self.tools):

            if chunk_type == "reasoning":
                accumulated_reasoning += chunk
                
            elif chunk_type == "content":
                accumulated += chunk
            yield chunk, chunk_type
            call = parse_tool_call(accumulated, list(self.tools.keys()))
            if call:
                tool_name, tool_call = call
                result = execute_tool_call(tool_call, self.tools[tool_name])
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
                if iteration + 1 < self.config.max_iterations:
                    if iteration + 1 == self.config.max_iterations - 1:
                        self.state.add_message(UserMessage(content="You have reached the maximum number of iterations. Please provide a final answer without further tool usage."))
                    return (yield from self.invoke(iteration + 1))
                else:
                    yield "\nMaximum iterations reached. Ending process.", "content"
        self.state.add_message(AssistantMessage(content=accumulated, reasoning_content=accumulated_reasoning))
        if self.config.auto_save:
            self.save()
        
    def instruct(self, instruction: str):
        self.state.add_message(UserMessage(content=instruction))
        for chunk, chunk_type in self.invoke():
            yield chunk, chunk_type

    def chat(self, reasoning_style: str = "italic blue", content_style: str = "cyan", tool_style: str = "magenta"):
        """Start an interactive chat session with the agent."""
        print("Starting chat session with the agent. Type 'exit' to quit.")
        try:
            while True:
                user_input = prompt("\nYou: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Bye :)")
                    break
                self.state.add_message(UserMessage(content=user_input))
                for chunk, chunk_type in self.invoke():
                    if chunk_type == "reasoning":
                        print(f"[{reasoning_style}]Agent is reasoning...[/]", end="", flush=True)
                    elif chunk_type == "content":
                        print(f"[{content_style}]{chunk}[/]", end="", flush=True)
                    elif chunk_type == "tool":
                        print()  # New line before tool output
                        print(panel.Panel(f"[{tool_style}]{chunk.result}[/]", title=chunk.name))
                        print()  # New line after tool output
                print()  # New line after agent response
        except KeyboardInterrupt:
            print("Bye :)")

    @classmethod
    def from_markdown(cls, filepath: str) -> "Agent":
        """Create an Agent instance from a markdown configuration file."""
        config, behavior = parse_markdown(filepath)
        return cls(**config, behavior=behavior)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """Create an Agent instance from a dictionary."""
        config_data = data.get("config", {})
        state_data = data.get("state", {})
        return cls(
            provider=config_data.get("provider", "openai"),
            model=config_data.get("model", "gpt-4.1-nano"),
            tools=config_data.get("tools", []),
            behavior=config_data.get("behavior", ""),
            max_iterations=config_data.get("max_iterations", 15),
            auto_save=config_data.get("auto_save", True),
            session_id=state_data.get("session_id", uuid().hex),
            created_at=state_data.get("created_at", datetime.now(timezone.utc).timestamp()),
            updated_at=state_data.get("updated_at", datetime.now(timezone.utc).timestamp()),
            messages=state_data.get("messages", None)
        )
    
    @classmethod
    def from_json(cls, file_path: str | Path) -> "Agent":
        """Create an Agent instance from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_session_id(cls, session_id: str) -> "Agent":
        """Create an Agent instance from a saved session ID."""
        file_path = Path.home() / ".vindao_agents" / "sessions" / f"{session_id}.json"
        return cls.from_json(file_path)

    def to_dict(self) -> dict:
        """Convert the agent's state to a dictionary."""
        return {
            "config": self.config.model_dump(),
            "state": self.state.model_dump()
        }

    def save(self, file_path: str | Path | None = None) -> str:
        """Save the agent's state to a file."""
        if not file_path:
            file_path = Path.home() / ".vindao_agents" / "sessions" / f"{self.state.session_id}.json"
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)
        return str(file_path)
        

    def __load_tools(self, tool_identifiers: list[str]) -> dict[str, Tool]:
        """Load tools based on their identifiers."""
        tools = {}
        for identifier in tool_identifiers:
            if callable(identifier):
                tool = Tool(identifier)
                tools[tool.name] = tool
            else:
                tools.update({name: Tool(func) for name, func in load_public_functions_from_identifier(identifier)})
        return tools
    
    def __build_initial_messages(self) -> list[Message]:
        """Build the initial messages for the agent."""
        system_message = self.config.behavior + "\n"
        system_message += f"You are using the model: {self.config.model}\n\n"
        base_path = Path.cwd() / "configs" / "tool_usage"
        if not base_path.exists():
            base_path = Path(__file__).parent / "configs" / "tool_usage"
        # load tool usage instructions
        tool_usage_path = base_path / f"{self.config.model}.md"
        if not tool_usage_path.exists():
            tool_usage_path = base_path / "default.md"
        system_message += tool_usage_path.read_text(encoding="utf-8")
        if len(self.tools) > 0:
            system_message += "\n\nAvailable functions:\n\n"
            for tool in self.tools.values():
                system_message += tool.source + "\n\n"
        return [SystemMessage(content=system_message)]
