"""Bash command execution tool."""


def bash(cmd: str):
    """Execute a bash command and return its output or error message."""
    import subprocess

    result = subprocess.run(cmd, check=False, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr
    return result.stdout
