"""Shared fixtures and configuration for pytest."""

# stdlib
from collections.abc import Generator
from pathlib import Path

# third party
import pytest


@pytest.fixture
def tmp_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    yield tmp_path


@pytest.fixture
def sample_tool():
    """Provide a sample tool function for testing."""

    def multiply(x: int, y: int) -> int:
        """Multiply two integers.
        
        Args:
            x: First integer
            y: Second integer
            
        Returns:
            The product of x and y
        """
        return x * y

    return multiply


@pytest.fixture
def sample_tool_with_exception():
    """Provide a sample tool that raises an exception."""

    def divide(x: int, y: int) -> float:
        """Divide two integers.
        
        Args:
            x: Numerator
            y: Denominator
            
        Returns:
            The quotient of x and y
        """
        return x / y

    return divide


@pytest.fixture
def mock_inference_adapter_factory():
    """Factory for creating mock inference adapters with custom responses."""

    class MockInferenceAdapter:
        """Mock inference adapter for testing."""

        def __init__(self, provider: str, model: str, responses: list = None):
            self.provider = provider
            self.model = model
            self.responses = responses or [("response", "content")]
            self.call_count = 0

        def complete_chat(self, messages, max_retries: int = 5, retry: int = 0):
            """Mock complete_chat method that yields predefined responses."""
            for chunk, chunk_type in self.responses:
                yield chunk, chunk_type
            self.call_count += 1

    def factory(responses: list = None):
        return lambda provider, model: MockInferenceAdapter(provider, model, responses)

    return factory
