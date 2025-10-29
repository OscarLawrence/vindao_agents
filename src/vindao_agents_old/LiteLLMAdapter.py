# Standard library imports
from typing import Generator, Tuple, Literal
import json
from time import sleep

# Third-party imports
from litellm import completion
from litellm.exceptions import RateLimitError

# Local imports
from .models.messages import Message
from .Tool import Tool
from .formatters.format_exception import format_exception

class LiteLLMAdapter:
    """Adapter wrapping litellm for multi-provider LLM async streaming with tool call support."""

    def __init__(self, provider: str, model: str):
        """Initialize adapter with provider and model configuration."""
        self.model_str = f"{provider}/{model}"

    def completion(self, messages: list[Message], tools: dict[str, Tool], max_retries: int = 5, retry: int = 0) -> Generator[Tuple[str, Literal['reasoning', 'content']], None, None]:
        """stream chat completion with reasoning and content separation.

        Note on tools parameter:
        We pass tool names (not full schemas) to satisfy provider requirements.
        Some providers reject tool messages (role="tool") if no tools were declared
        in the initial completion call. While we use custom @syntax parsing instead
        of native function calling, we still need to declare tool existence to avoid
        validation errors when tool results are included in the conversation.
        """
        formatted_messages = self.__formatMessages(messages)

        try:
            response = completion(
                model=self.model_str,
                messages=formatted_messages,
                stream=True,
                tools=list(tools.keys()) if tools else None
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                delta_reasoning_content = delta.get("reasoning_content", None)
                if delta_reasoning_content:
                    yield delta_reasoning_content, "reasoning"
                delta_content = delta.get("content", None)
                if delta_content:
                    yield delta_content, "content"
        except RateLimitError as e:
            if retry < max_retries:
                print(f"Rate limit exceeded. Retrying {retry + 1}/{max_retries}...")
                sleep(2 ** retry)  # Exponential backoff
                yield from self.completion(messages, tools, max_retries, retry + 1)
            else:
                raise e
        except Exception as e:
            if retry < max_retries:
                print(f"{format_exception(e)}. Retrying {retry + 1}/{max_retries}...")
                sleep(2 ** retry)  # Exponential backoff
                yield from self.completion(messages, tools, max_retries, retry + 1)
            else:
                raise e


    def __formatMessages(self, messages: list[Message]) -> list[dict]:
        """Convert internal message objects to litellm-compatible format with tool call handling."""
        formatted_messages = []
        for message in messages:
            if message.role == "system":
                formatted_messages.append({"role": "system", "content": message.content})
            elif message.role == "user":
                formatted_messages.append({"role": "user", "content": message.content})
            elif message.role == "assistant":
                formatted_messages.append({"role": "assistant", "content": message.content})
            elif message.role == "tool":
                formatted_messages.append({"role": "user", "name": message.name, "content": message.content})
        return formatted_messages