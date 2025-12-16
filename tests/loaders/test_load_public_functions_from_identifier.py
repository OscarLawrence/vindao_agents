"""Tests for load_public_functions_from_identifier."""

# third party

# local
from vindao_agents.loaders.load_public_functions_from_identifier import load_public_functions_from_identifier


class TestLoadPublicFunctions:
    def test_load_functions(self):
        # Assuming there's a module named 'sample_module' with public functions
        functions = load_public_functions_from_identifier('vindao_agents.formatters.format_exception')
        function_names = [name for name, _ in functions]
        assert 'format_exception' in function_names
        assert 'TestFormatException' not in function_names
        assert len(functions) == 1  # Only one public function expected
