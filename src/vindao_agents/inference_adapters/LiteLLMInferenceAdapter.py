"""Inference adapter for LiteLLM model integration."""

# stdlib
from time import sleep

# third party
import litellm

# local
from vindao_agents.inference_adapters.InferenceAdapter import InferenceAdapter
from vindao_agents.models.messages import MessageType
from vindao_agents.formatters import format_exception

class LiteLLMInferenceAdapter(InferenceAdapter):


    def __init__(self, provider: str, model: str):
        """Initialize adapter with provider and model configuration."""
        self.model_str = f"{provider}/{model}"

    def completion(self, messages: list[MessageType], max_retries: int = 5, retry: int = 0):
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
                print(f"{format_exception(e)}. Retrying {retry + 1}/{max_retries}...")
                sleep(2 ** retry)  # Exponential backoff
                yield from self.completion(messages, max_retries, retry + 1)
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
    
class TestLiteLLMInferenceAdapter:

    adapter = LiteLLMInferenceAdapter(provider="ollama", model="qwen2.5:0.5b")

    def test_formatMessages(self):
        from vindao_agents.models.messages import SystemMessage, UserMessage, AssistantMessage, ToolMessage

        messages = [
            SystemMessage(content="System content"),
            UserMessage(content="User content"),
            AssistantMessage(content="Assistant content"),
            ToolMessage(content="Tool content", name="sample_tool")
        ]

        formatted = self.adapter._formatMessages(messages)
        assert formatted[0]["role"] == "system"
        assert formatted[1]["role"] == "user"
        assert formatted[2]["role"] == "assistant"
        assert formatted[3]["role"] == "user"  # Tool message role changed to user
        assert formatted[3]["name"] == "sample_tool"

    def test_completion_retry(self, monkeypatch):
        from vindao_agents.models.messages import UserMessage
        from unittest.mock import MagicMock
        import litellm

        messages = [UserMessage(content="Test content")]

        call_count = {"count": 0}

        def mock_completion(*args, **kwargs):
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise Exception("Simulated failure")

            # Create a proper mock response
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta = MagicMock()
            mock_chunk.choices[0].delta.get = lambda key, default=None: "Final content" if key == "content" else default

            return iter([mock_chunk])

        # Patch litellm.completion function
        monkeypatch.setattr(litellm, "completion", mock_completion)

        results = list(self.adapter.completion(messages, max_retries=5))
        assert results == [("Final content", "content")]
        assert call_count["count"] == 3  # Ensure it retried twice before succeeding
    
