"""Tools available to the setup agent for helping users configure the system."""

from pathlib import Path


def create_agent_file(name: str, provider: str, model: str, tools: str, behavior: str) -> str:
    """Create an agent markdown configuration file.

    Args:
        name: Name of the agent (will be used as filename)
        provider: LLM provider (e.g., 'openai', 'anthropic')
        model: Model identifier (e.g., 'gpt-4', 'claude-sonnet-4-5')
        tools: Comma-separated list of tool modules (e.g., 'tools.bash,tools.file_ops')
        behavior: Description of the agent's behavior and purpose

    Returns:
        Success message with file path
    """
    agents_dir = Path.home() / ".vindao_agents" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Clean up the name for filename
    filename = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    agent_file = agents_dir / f"{filename}.md"

    # Parse tools list
    tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    tools_yaml = "\n".join([f"- {tool}" for tool in tool_list]) if tool_list else "[]"

    # Create markdown content
    content = f"""---
provider: {provider}
model: {model}
tools:
{tools_yaml}
---
{behavior}
"""

    agent_file.write_text(content, encoding="utf-8")
    return f"Created agent file: {agent_file}"


def create_tool_file(name: str, code: str) -> str:
    """Create a Python tool file.

    Args:
        name: Name of the tool (will be used as filename without .py extension)
        code: Python code defining the tool function(s)

    Returns:
        Success message with file path
    """
    tools_dir = Path.home() / ".vindao_agents" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    # Clean up the name for filename
    filename = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    if not filename.endswith(".py"):
        filename += ".py"

    tool_file = tools_dir / filename

    tool_file.write_text(code, encoding="utf-8")
    return f"Created tool file: {tool_file}"


def list_available_tools() -> str:
    """List all available tool modules in the system.

    Returns:
        Formatted list of available tools
    """
    # Built-in tools from the package
    builtin_tools = [
        "vindao_agents.tools (bash, file operations)",
    ]

    # User's custom tools
    tools_dir = Path.home() / ".vindao_agents" / "tools"
    custom_tools = []

    if tools_dir.exists():
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.stem != "__init__":
                custom_tools.append(f"~/.vindao_agents/tools/{tool_file.name}")

    result = "Built-in tools:\n"
    for tool in builtin_tools:
        result += f"  - {tool}\n"

    if custom_tools:
        result += "\nCustom tools:\n"
        for tool in custom_tools:
            result += f"  - {tool}\n"
    else:
        result += "\nNo custom tools created yet."

    return result


def get_setup_status() -> str:
    """Get the current setup status.

    Returns:
        Status information about the user's setup
    """
    base_dir = Path.home() / ".vindao_agents"
    agents_dir = base_dir / "agents"
    tools_dir = base_dir / "tools"

    agent_count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
    tool_count = len([f for f in tools_dir.glob("*.py") if f.stem != "__init__"]) if tools_dir.exists() else 0

    status = f"""Setup Status:
- Configuration directory: {base_dir}
- Agents created: {agent_count}
- Custom tools created: {tool_count}
"""

    if agent_count > 0:
        status += "\nAvailable agents:\n"
        for agent_file in agents_dir.glob("*.md"):
            status += f"  - {agent_file.stem}\n"

    return status
