"""Multi-file reader tool."""
from .read_file import read_file


def read_files(*paths: str) -> str:
    """Read and return the contents of multiple files."""
    response = ""
    for file_path in paths:
        response += f"\n# {file_path}\n"
        try:
            response += read_file(file_path)
        except Exception as e:
            response += f"{e.with_traceback(None)}"
    return response
