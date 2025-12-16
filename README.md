# Vindao Agents

An extensible AI agent framework for building interactive, tool-enabled conversational agents with streaming support.

## Features

- 🤖 **Multiple Agent Support** - Create and manage different AI agents with unique behaviors and capabilities
- 🔧 **Tool Integration** - Easily add custom tools (bash commands, file operations, etc.) to your agents
- 💬 **Interactive Chat** - Built-in CLI for interactive conversations with your agents
- 📝 **Markdown Configuration** - Define agents using simple markdown files with YAML frontmatter
- 🔄 **Session Management** - Save and resume conversations with persistent state
- ⚡ **Streaming Responses** - Real-time streaming output with rich formatting
- 🎯 **Multiple LLM Support** - Works with OpenAI, Anthropic, Ollama, and more via LiteLLM
- 🔌 **Extensible Architecture** - Plugin-based system for inference adapters, tool parsers, and storage

## Installation

Install from PyPI:

```bash
pip install vindao_agents
```

Or using uv (recommended):

```bash
uv pip install vindao_agents
```

For development installation:

```bash
git clone https://github.com/vindao/vindao_agents.git
cd vindao_agents
uv pip install -e ".[dev]"
```

## Quick Start

### Using the CLI

Start a chat with the default agent:

```bash
agent
```

Use a specific agent:

```bash
agent --agent Developer
```

List available agents:

```bash
agent --list
```

Resume a previous session:

```bash
agent --resume <session-id>
```

### Using the Python API

```python
from vindao_agents import Agent

# Create an agent from a predefined template
agent = Agent.from_name("DefaultAgent")

# Start an interactive chat
agent.chat()
```

## Creating Custom Agents

Agents are defined using markdown files with YAML frontmatter. Create a file named `MyAgent.md`:

```markdown
---
provider: openai
model: gpt-4
tools:
- tools.bash
- tools.file_ops
tools_with_source: false
---

You are a helpful assistant with expertise in software development.
You value clean code and best practices.
```

Then use it:

```python
from vindao_agents import Agent

agent = Agent.from_markdown("MyAgent.md")
agent.chat()
```

## Configuration

### Agent Configuration

- **provider**: LLM provider (openai, anthropic, ollama, etc.)
- **model**: Model identifier
- **tools**: List of tool modules to enable
- **tools_with_source**: Include source code in tool descriptions
- **max_iterations**: Maximum reasoning iterations
- **auto_save**: Automatically save session state

### Environment Variables

Configure your LLM API keys:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
# Or use .env file
```

Custom data directory:

```bash
export USER_DATA_DIR="/path/to/data"
```

## Available Tools

### Built-in Tools

- **bash** - Execute shell commands
- **file_ops** - File operations (read, write, search, etc.)

### Adding Custom Tools

```python
from vindao_agents import Agent, Tool

def my_custom_tool(query: str) -> str:
    """
    My custom tool description.

    Args:
        query: The query parameter

    Returns:
        The result
    """
    return f"Processed: {query}"

agent = Agent(
    name="CustomAgent",
    tools=["tools.bash"],  # Use existing tools
)

# Add custom tool
agent.tools["my_tool"] = Tool(my_custom_tool)
agent.chat()
```

## API Reference

### Agent Class

```python
Agent(
    name: str = 'Momo',
    provider: str = 'ollama',
    model: str = 'qwen2.5:0.5b',
    tools: list[str] = [],
    behavior: str = "",
    max_iterations: int = 15,
    auto_save: bool = True,
)
```

### Methods

- `agent.chat()` - Start interactive chat session
- `agent.instruct(instruction: str)` - Send single instruction
- `Agent.from_name(name: str)` - Load predefined agent
- `Agent.from_markdown(path: str)` - Load agent from markdown
- `Agent.from_session_id(session_id: str)` - Resume session

## Architecture

```
vindao_agents/
├── Agent.py              # Main agent orchestrator
├── Tool.py               # Tool wrapper
├── models/               # Data models
│   ├── agent.py
│   ├── messages.py
│   └── tool.py
├── InferenceAdapters/    # LLM provider adapters
├── ToolParsers/          # Tool call parsing
├── AgentStores/          # State persistence
├── tools/                # Built-in tools
│   ├── bash.py
│   └── file_ops/
├── agents/               # Predefined agents
│   ├── DefaultAgent.md
│   ├── Developer.md
│   └── ...
└── utils/                # Utilities
```

## Examples

### Programmatic Agent Usage

```python
from vindao_agents import Agent

# Create agent with custom configuration
agent = Agent(
    name="CodeReviewer",
    provider="anthropic",
    model="claude-sonnet-4-5",
    tools=["tools.file_ops"],
    behavior="You are a code reviewer focused on quality and security.",
    max_iterations=10
)

# Process instruction with streaming
for chunk, chunk_type in agent.instruct("Review the authentication code"):
    if chunk_type == "content":
        print(chunk, end="", flush=True)
```

### Custom Tool Module

Create `my_tools.py`:

```python
def search_database(query: str) -> str:
    """
    Search the database for information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Your implementation
    return f"Results for: {query}"

def analyze_data(data_id: str) -> dict:
    """
    Analyze data by ID.

    Args:
        data_id: Data identifier

    Returns:
        Analysis results
    """
    return {"status": "analyzed", "id": data_id}
```

Use in agent:

```markdown
---
provider: openai
model: gpt-4
tools:
- my_tools
---
You are a data analysis assistant.
```

## Development

### Running Tests

```bash
pytest
```

### Project Structure

- `src/vindao_agents/` - Main package
- `tests/` - Test suite
- `pyproject.toml` - Project configuration

## License

This project is licensed under a Custom License with commercial profit-sharing requirements. See [LICENSE](LICENSE) for details.

**Summary:**
- ✅ Free for non-commercial use
- ✅ Modify and distribute freely
- ⚠️ Commercial use requires 1% profit-sharing agreement

For commercial licensing inquiries, contact: vindao@outlook.com

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

```bash
git clone https://github.com/vindao/vindao_agents.git
cd vindao_agents
uv pip install -e ".[dev]"
```

## Support

- GitHub Issues: https://github.com/vindao/vindao_agents/issues
- Email: vindao@outlook.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
