"""Load message objects from a list of dictionaries."""

# local
from vindao_agents.models.messages import AssistantMessage, MessageType, SystemMessage, ToolMessage, UserMessage


def load_messages_from_dicts(dicts: list[dict]) -> list[MessageType]:
    messages: list[MessageType] = []
    for message_dict in dicts:
        message_type = message_dict.get("role")
        if message_type == "system":
            messages.append(SystemMessage.model_validate(message_dict))
        elif message_type == "assistant":
            messages.append(AssistantMessage.model_validate(message_dict))
        elif message_type == "user":
            messages.append(UserMessage.model_validate(message_dict))
        elif message_type == "tool":
            messages.append(ToolMessage.model_validate(message_dict))
        else:
            raise ValueError(f"Unknown message type: {message_type}")
    return messages
