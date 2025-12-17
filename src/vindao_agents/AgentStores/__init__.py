

from .AgentStore import AgentStore as AgentStore
from .JsonAgentStore import JsonAgentStore as JsonAgentStore

stores = {
    "json": JsonAgentStore,
}
