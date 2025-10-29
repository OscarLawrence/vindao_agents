
def format_exception(exc: Exception) -> str:
    """Format an exception into a readable string."""
    return f"{type(exc).__name__}: {str(exc)}"