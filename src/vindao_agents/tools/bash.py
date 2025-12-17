"""Bash command execution tool."""


def bash(cmd: str):
    """Execute a bash command and return its output or error message.

    Security Note: This function executes shell commands by design as it is
    core functionality for an AI agent framework. Users should be aware that
    agents can execute arbitrary commands and should only be used in trusted
    environments with appropriate safeguards.

    Args:
        cmd: The bash command to execute

    Returns:
        stdout if successful, stderr if failed
    """
    import subprocess  # nosec B404: subprocess is required for bash tool functionality

    # nosec B602: shell=True is required for bash command execution in agent framework
    # Users should only use this tool in trusted environments
    result = subprocess.run(cmd, check=False, shell=True, capture_output=True, text=True)  # nosec
    if result.returncode != 0:
        return result.stderr
    return result.stdout
