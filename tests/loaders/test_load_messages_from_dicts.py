"""Tests for load_messages_from_dicts."""

# third party

# local
from vindao_agents.loaders.load_messages_from_dicts import load_messages_from_dicts
from vindao_agents.models.messages import AssistantMessage, SystemMessage, ToolMessage, UserMessage


class TestLoadMessagesFromDicts:
    def test_load_messages_from_dicts(self):
        tool_call_dict = {"name": "test_tool", "call": "test_call", "result": "test_result"}
        dicts = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"},
            {"role": "tool", "content": "Tool message", "name": "test_tool", "tool_call": tool_call_dict},
        ]
        messages = load_messages_from_dicts(dicts)
        assert len(messages) == 4
        assert isinstance(messages[0], SystemMessage)
        assert isinstance(messages[1], UserMessage)
        assert isinstance(messages[2], AssistantMessage)
        assert isinstance(messages[3], ToolMessage)
