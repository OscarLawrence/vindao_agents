"""Multi-file reader tool."""
from ...formatters.format_exception import format_exception
from .read_file import read_file


def read_files(*paths: str) -> str:
    """Read and return the contents of multiple files."""
    response = ""
    for file_path in paths:
        response += f"\n# {file_path}\n"
        try:
            response += read_file(file_path)
        except Exception as e:
            response += format_exception(e)
    return response
