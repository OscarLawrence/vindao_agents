"""Inference adapter for LiteLLM model integration."""

# stdlib
from time import sleep

# third party
import litellm

from vindao_agents.formatters import format_exception

# local
from vindao_agents.InferenceAdapters.InferenceAdapter import InferenceAdapter
from vindao_agents.models.messages import MessageType
from vindao_agents.utils import get_default_logger


class LiteLLMInferenceAdapter(InferenceAdapter):


    def __init__(self, provider: str, model: str):
        """Initialize adapter with provider and model configuration."""
        self.model_str = f"{provider}/{model}"
        self.logger = get_default_logger()

    def complete_chat(self, messages: list[MessageType], max_retries: int = 5, retry: int = 0):
        formatted_messages = self._formatMessages(messages)
        try:
            response = litellm.completion(
                model=self.model_str,
                messages=formatted_messages,
                stream=True
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                delta_reasoning_content = delta.get("reasoning_content", None)
                if delta_reasoning_content:
                    yield delta_reasoning_content, "reasoning"
                delta_content = delta.get("content", None)
                if delta_content:
                    yield delta_content, "content"
        except Exception as e:
            if retry < max_retries:
                self.logger.warning(f"{format_exception(e)}. Retrying {retry + 1}/{max_retries}...")
                sleep(2 ** retry)  # Exponential backoff
                yield from self.complete_chat(messages, max_retries, retry + 1)
            else:
                raise e


    def _formatMessages(self, messages: list[MessageType]) -> list[dict]:
        """Convert internal message objects to litellm-compatible format with tool call handling."""
        formatted_messages = []
        for message in messages:
            if message.role != "system":
                msg = message.model_dump(include={"role", "content", "name"})
                if message.role == "tool":
                    # For tool messages, set role to "user" and include tool name
                    # This is to stay provider and model agnostic
                    msg["role"] = "user"
                formatted_messages.append(msg)
            else:
                formatted_messages.append(message.model_dump())

        return formatted_messages
