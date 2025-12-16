# Agent Tests

This directory contains comprehensive tests for the `Agent` class in the vindao_agents package.

## Test Coverage

The test suite covers the following aspects of the Agent class:

### 1. Initialization (`TestAgentInitialization`)
- Default initialization with minimal parameters
- Custom initialization with all parameters
- Initialization with existing session data and messages

### 2. Invoke Method (`TestAgentInvoke`)
- Simple responses without tool calls
- Responses with reasoning content
- Tool call execution and result handling
- Disabled tool calls using the `@DISABLE_TOOL_CALL@` marker
- Maximum iteration warnings

### 3. Instruct Method (`TestAgentInstruct`)
- Adding user messages to state
- Yielding chunks from invoke

### 4. Chat Method (`TestAgentChat`)
- Interactive chat with exit commands
- Keyboard interrupt handling

### 5. Save Functionality (`TestAgentSave`)
- Manual save method invocation
- Custom save paths
- Auto-save after invoke

### 6. Factory Methods
- **`TestAgentFromDict`**: Creating agents from dictionaries
- **`TestAgentFromJson`**: Loading agents from JSON files
- **`TestAgentFromSessionId`**: Loading agents by session ID
- **`TestAgentFromMarkdown`**: Creating agents from markdown files with frontmatter
- **`TestAgentFromName`**: Loading predefined agents by name

### 7. Tool Management (`TestAgentLoadTools`)
- Loading tools from module identifiers
- Handling empty tool lists

### 8. System Message Building (`TestAgentBuildSystemMessage`)
- Including agent name in system message
- Including behavior in system message
- Including tool instructions in system message

### 9. State Management (`TestAgentStateManagement`)
- Timestamp updates when messages are added
- Maintaining message order

### 10. Configuration (`TestAgentConfiguration`)
- Configuration value persistence
- Default configuration values

## Running the Tests

Run all Agent tests:
```bash
pytest tests/test_agent.py -v
```

Run a specific test class:
```bash
pytest tests/test_agent.py::TestAgentInitialization -v
```

Run a specific test:
```bash
pytest tests/test_agent.py::TestAgentInitialization::test_default_initialization -v
```

Run tests with coverage:
```bash
pytest tests/test_agent.py --cov=vindao_agents.Agent --cov-report=html
```

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

- `tmp_path`: Provides temporary directories for isolated testing
- `sample_tool`: A simple multiplication tool for testing
- `sample_tool_with_exception`: A tool that can raise exceptions for error testing
- `mock_inference_adapter_factory`: Factory for creating mock inference adapters with custom responses

## Mocking Strategy

The tests use extensive mocking to isolate the Agent class functionality:

1. **Inference Adapters**: Mocked to return predefined responses without requiring actual LLM API calls
2. **Tool Execution**: Mocked to control tool call results
3. **File I/O**: Uses `tmp_path` fixtures to avoid side effects on the filesystem
4. **External Dependencies**: Module loading and other external dependencies are mocked where appropriate

## Test Data

Test data includes:

- Sample messages (System, User, Assistant, Tool)
- Sample tool calls in the format `@tool_name(args)`
- Mock inference responses with content and reasoning chunks
- Sample configuration data for JSON and markdown loading

## Best Practices

1. **Isolation**: Each test is independent and doesn't affect others
2. **Clarity**: Test names clearly describe what they test
3. **Coverage**: Tests cover both success and edge cases
4. **Mocking**: External dependencies are mocked to ensure fast, reliable tests
5. **Organization**: Tests are organized into logical test classes by functionality

## Known Limitations

- Some integration tests with actual LLM providers are not included (to keep tests fast and deterministic)
- Tool call parsing edge cases may need additional coverage
- Concurrent execution scenarios are not thoroughly tested

## Contributing

When adding new features to the Agent class:

1. Add corresponding tests in the appropriate test class
2. Ensure all tests pass before submitting
3. Aim for high code coverage (target: >90%)
4. Use descriptive test names following the pattern: `test_<what>_<condition>`
