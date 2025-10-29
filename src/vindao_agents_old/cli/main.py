
# Third-party imports
from prompt_toolkit import prompt
from rich import print, panel

# Local imports
from vindao_agents.models.messages import UserMessage

class CLI:

    def __init__(self, agent):
        self.agent = agent

    def chat(self, reasoning_style: str = "italic blue", content_style: str = "cyan", tool_style: str = "magenta"):
        """Start an interactive chat session with the agent."""
        print("Starting chat session with the agent. Type 'exit' to quit.")
        try:
            while True:
                user_input = prompt("\nYou: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Bye :)")
                    break
                self.agent.state.add_message(UserMessage(content=user_input))
                for chunk, chunk_type in self.agent.invoke():
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

