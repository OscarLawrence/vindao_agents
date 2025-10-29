"""Agent orchestrator for managing AI agent interactions and tool execution."""
# stdlib
from uuid import uuid4 as uuid
from datetime import datetime, timezone
from pathlib import Path
from os import getenv
from dotenv import load_dotenv

# local
from vindao_agents.models.messages import MessageType, SystemMessage, UserMessage, AssistantMessage, ToolMessage
from vindao_agents.models.tool import ToolCall
from .models.agent import AgentConfig, AgentState
from vindao_agents.Tool import Tool
from vindao_agents.loaders import load_public_functions_from_identifier, load_system_message_template
from vindao_agents.formatters import format_prompt
from vindao_agents.parsers import parse_markdown_with_frontmatter, parse_tool_call
from vindao_agents.executors import execute_tool_call
from vindao_agents.inference_adapters import adapters
from vindao_agents.storage import save_agent_state

load_dotenv()

class Agent:

    tools: dict[str, Tool]
    config: AgentConfig
    state: AgentState

    def __init__(
            self,
            name: str = 'Momo',
            provider: str = 'ollama',
            model: str = 'qwen2.5:0.5b',
            tools: list[str] = [],
            behavior: str = "",
            max_iterations: int = 15,
            auto_save: bool = True,
            user_data_dir: str | Path = getenv("USER_DATA_DIR", Path.home() / ".vindao_agents"),
            system_prompt_data: dict | None = None,
            tools_with_source: bool = True,
            session_id: str = uuid().hex,
            created_at: float = datetime.now(timezone.utc).timestamp(),
            updated_at: float = datetime.now(timezone.utc).timestamp(),
            messages: list[MessageType] | None = None,
            inference_adapter: str = "litellm",
            
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
            inference_adapter=inference_adapter,
        )
        
        self.tools = self.__load_tools(tools)
        if not messages:
            messages = [self.__build_system_message()]
        self.state = AgentState(
            session_id=session_id,
            created_at=created_at,
            updated_at=updated_at,
            messages=messages
        )
        self.adapter = adapters[self.config.inference_adapter](provider=self.config.provider, model=self.config.model)

    def invoke(self, iteration: int = 0, max_iterations: int | None = None):
        """Invoke the agent's reasoning and tool usage process."""
        if max_iterations is None:
            max_iterations = self.config.max_iterations
        accumulated_reasoning = ""
        accumulated = ""
        iteration += 1
        tool_call_enabled = True

        if iteration == max_iterations - 1:
            self.state.add_message(UserMessage(content="You have reached the maximum number of iterations. Please provide a summary without further tool usage."))
            tool_call_enabled = False

        for chunk, chunk_type in self.adapter.completion(self.state.messages):

            if chunk_type == "reasoning":
                accumulated_reasoning += chunk
                
            elif chunk_type == "content":
                accumulated += chunk
            yield chunk, chunk_type
            if accumulated.startswith('@RESPOND@'):
                tool_call_enabled = False
            if tool_call_enabled:
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
                    if iteration < max_iterations:
                        return (yield from self.invoke(iteration + 1, max_iterations=max_iterations))
                    else:
                        yield "\nMaximum iterations reached. Ending process.", "content"
        if accumulated.startswith('@RESPOND@'):
            accumulated = accumulated.replace('@RESPOND@', '', 1).lstrip()
        self.state.add_message(AssistantMessage(content=accumulated, reasoning_content=accumulated_reasoning))
        if self.config.auto_save:
            self.save()
        
    def instruct(self, instruction: str):
        self.state.add_message(UserMessage(content=instruction))
        for chunk, chunk_type in self.invoke():
            yield chunk, chunk_type

    def chat(self):
        """Start an interactive chat session with the agent."""
        print("Starting chat session with the agent. Type 'exit' to quit.")
        try:
            while True:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting chat session.")
                    break
                for chunk, chunk_type in self.instruct(user_input):
                    if chunk_type in ["content", "reasoning"]:
                        print(chunk, end='', flush=True)
                    elif chunk_type == "tool":
                        print(f" =>\n{chunk.result}\n")
                print("\n")  # Newline after agent response
        except KeyboardInterrupt:
            print("\nChat session interrupted. Goodbye!")

    def save(self, path: str | Path | None = None) -> None:
        """Save the agent's state to a file."""
        save_agent_state(self, path)

    @classmethod
    def from_markdown(cls, path: str | Path) -> "Agent":
        """Create an Agent instance from a markdown file with frontmatter."""
        metadata, behavior = parse_markdown_with_frontmatter(path)
        return cls(
            provider=metadata.get("provider", "ollama"),
            model=metadata.get("model", "qwen2.5:0.5b"),
            tools=metadata.get("tools", []),
            behavior=behavior,
            max_iterations=metadata.get("max_iterations", 15),
            auto_save=metadata.get("auto_save", True),
            user_data_dir=metadata.get("user_data_dir", Path.home() / ".vindao_agents"),
            system_prompt_data=metadata.get("system_prompt_data", {}),
            tools_with_source=metadata.get("tools_with_source", True),
        )
        

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
        content = format_prompt(template, {**self.config.system_prompt_data, "model": self.config.model, "behavior": self.config.behavior, "name": self.config.name, "tools": tool_str.strip()})
        return SystemMessage(content=content)
