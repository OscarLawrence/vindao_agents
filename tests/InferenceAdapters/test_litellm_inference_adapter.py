"""Tests for LiteLLM Inference Adapter."""

# third party
import pytest

# local
from vindao_agents.InferenceAdapters.LiteLLMInferenceAdapter import LiteLLMInferenceAdapter
from vindao_agents.models.messages import SystemMessage, UserMessage, AssistantMessage, ToolMessage
from vindao_agents.models.tool import ToolCall


class TestLiteLLMInferenceAdapter:

    adapter = LiteLLMInferenceAdapter(provider="ollama", model="qwen2.5:0.5b")

    def test_formatMessages(self):
        tool_call = ToolCall(name="sample_tool", call="test_call", result="test_result")
        messages = [
            SystemMessage(content="System content"),
            UserMessage(content="User content"),
            AssistantMessage(content="Assistant content"),
            ToolMessage(content="Tool content", name="sample_tool", tool_call=tool_call)
        ]

        formatted = self.adapter._formatMessages(messages)
        assert formatted[0]["role"] == "system"
        assert formatted[1]["role"] == "user"
        assert formatted[2]["role"] == "assistant"
        assert formatted[3]["role"] == "user"  # Tool message role changed to user
        assert formatted[3]["name"] == "sample_tool"

    def test_completion_retry(self, monkeypatch):
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

        results = list(self.adapter.complete_chat(messages, max_retries=5))
        assert results == [("Final content", "content")]
        assert call_count["count"] == 3  # Ensure it retried twice before succeeding
