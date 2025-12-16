# vindao_agents Framework - Refactoring Plan

**Date:** 2025-12-16
**Status:** Phase 1 - Foundation Work

---

## ✅ COMPLETED

### Quick Fixes
- [x] **#12: Unclear variable names** - `accumulated` → `accumulated_content` in `Agent.py:95` (2025-12-16)
- [x] **#1: Inline tests removed** - Extracted ~400 lines of test code to hierarchical test structure (2025-12-16)
- [x] **#2: Fixed error handling** - `read_files.py` now uses `format_exception()` properly (2025-12-16)
- [x] **#10: Fixed exception duplication** - Removed duplicate exception appending in `format_exception.py` (2025-12-16)

### Phase 1: Foundation Work
- [x] **Phase 1.1: Centralize Path Resolution** - Created `utils/path_resolution.py` with `resolve_path()` and `resolve_path_with_fallbacks()`, updated `Agent.from_name()` and `load_system_message_template.py`, added 15 comprehensive tests (2025-12-16)

### Design Decisions (Not Issues)
- **Message role mutation (prev #4)** - Intentional for model-agnostic tool calling ✓
- **Registry pattern (prev #5)** - Intentional for user extensibility ✓
- **Package naming (prev #11)** - Intentional: PascalCase = abstractions, snake_case = functional ✓
- **Shell injection (prev #13)** - `shell=True` intentional for agent tool usage ✓

---

## 🎯 REFACTORING PHASES

### Phase 1: Foundation Work (1-2 days)

These changes establish the foundation for larger refactorings:

#### 1.1 Centralize Path Resolution ✅ COMPLETED
**Issue #7** | `Agent.py`, `load_system_message_template.py`

**Problem:**
- `Agent.from_name()` has dual-path logic (cwd/agents → package/agents)
- `load_system_message_template.py` has nested if/else path checks
- Same problem solved differently across multiple files

**Implementation:**
```python
# Created: src/vindao_agents/utils/path_resolution.py
def resolve_path(filename: str, search_dirs: list[str | Path]) -> Path:
    """Resolve a file path by searching through directories in priority order."""
    for directory in search_dirs:
        candidate = Path(directory) / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(...)

def resolve_path_with_fallbacks(
    filenames: list[str],
    search_dirs: list[str | Path]
) -> Path:
    """Resolve with multiple filename fallbacks."""
    for filename in filenames:
        for directory in search_dirs:
            candidate = Path(directory) / filename
            if candidate.exists():
                return candidate
    raise FileNotFoundError(...)
```

**Results:**
- ✅ Created `src/vindao_agents/utils/path_resolution.py` with both functions
- ✅ Created `src/vindao_agents/utils/__init__.py`
- ✅ Updated `Agent.from_name()` - reduced from 7 to 6 lines, clearer logic
- ✅ Updated `load_system_message_template.py` - eliminated nested if/else
- ✅ Created comprehensive test suite with 15 tests
- ✅ All 79 tests passing (64 original + 15 new)

**Note:** `load_agent_from_markdown.py` didn't require changes - it takes paths directly without resolution logic.

---

#### 1.2 Add Logging Framework
**Issue #6d** | `Agent.py`, framework-wide

**Problem:**
- Direct `print()` statements on lines 145-147, 152-153 in Agent
- No log levels, no structured logging
- Cannot disable or redirect output
- Makes Agent unusable in non-console environments (APIs, tests)

**Fix:**
```python
# Create: src/vindao_agents/utils/logger.py
import logging
from typing import Protocol

class AgentLogger(Protocol):
    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...

# Provide default logger but allow injection
def get_default_logger(name: str = "vindao_agents") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

**Impact:**
- Enables proper logging infrastructure
- **Required before Phase 2** (Agent refactoring)
- Allows users to control output

**Files to update:**
- Create `src/vindao_agents/utils/logger.py`
- Update `Agent.__init__()` to accept optional logger
- Replace print statements with logging calls throughout codebase

---

### Phase 2: Core Refactoring (2-3 days)

These changes address architectural issues and improve maintainability:

#### 2.1 Refactor Agent Class - Extract I/O
**Issue #3** | `Agent.py:141-148`

**Problem:**
- Agent directly prints output, making it untestable in non-console environments
- Cannot use Agent in APIs, background jobs, or tests
- Violates separation of concerns

**Current problematic code:**
```python
def instruct(self, instruction: str):
    self.state.add_message(UserMessage(content=instruction))
    for chunk, chunk_type in self.invoke():
        if chunk_type in ["content", "reasoning"]:
            print(chunk, end='', flush=True)  # ❌ Hard-coded I/O
        elif chunk_type == "tool":
            print(f" =>\n{chunk.result}\n")  # ❌ Hard-coded I/O
        yield chunk, chunk_type
```

**Fix:**
Agent should only orchestrate and yield events. Let callers decide how to display:

```python
# Agent.py - No print statements
def instruct(self, instruction: str):
    """Instruct agent and yield all events for caller to handle."""
    self.state.add_message(UserMessage(content=instruction))
    yield from self.invoke()

# New: src/vindao_agents/formatters/console_formatter.py
class ConsoleFormatter:
    """Formats and prints agent events to console."""

    def __init__(self, logger: AgentLogger):
        self.logger = logger

    def display_event(self, chunk, chunk_type):
        if chunk_type in ["content", "reasoning"]:
            self.logger.info(chunk)
        elif chunk_type == "tool":
            self.logger.info(f" =>\n{chunk.result}\n")

# Usage
agent = Agent(...)
formatter = ConsoleFormatter(logger)
for chunk, chunk_type in agent.instruct("Do something"):
    formatter.display_event(chunk, chunk_type)
```

**Impact:**
- Agent becomes usable in any context
- Users can implement custom formatters
- Easier to test

**Dependencies:** Requires Phase 1.2 (Logging Framework)

**Files to update:**
- `Agent.instruct()` - remove print statements
- `Agent.chat()` - update to use formatter
- Create `src/vindao_agents/formatters/console_formatter.py`
- Update examples to show proper usage

---

#### 2.2 Extract MessageBuilder
**Issue #6c** | `Agent.py:224-231`

**Problem:**
- System message construction buried in Agent
- Mixes template loading, tool serialization, parser instructions
- Hard to test independently
- Agent has too many responsibilities

**Current code:**
```python
def __build_system_message(self) -> SystemMessage:
    template = load_system_message_template(self.config.model, self.config.user_data_dir)
    tool_str = ""
    for tool in self.tools.values():
        tool_str += tool.to_instruction(include_source=self.config.tools_with_source)
    parser_instructions = self.parser.get_instructions()
    content = format_prompt(template, {**self.config.system_prompt_data, ...})
    return SystemMessage(content=content)
```

**Fix:**
```python
# Create: src/vindao_agents/builders/message_builder.py
class MessageBuilder:
    """Builds system messages from templates and configuration."""

    def build_system_message(
        self,
        model: str,
        tools: dict[str, Tool],
        parser: ToolParser,
        config: AgentConfig
    ) -> SystemMessage:
        template = load_system_message_template(model, config.user_data_dir)
        tool_str = self._serialize_tools(tools, config.tools_with_source)
        parser_instructions = parser.get_instructions()
        content = format_prompt(template, {
            **config.system_prompt_data,
            "model": model,
            "behavior": config.behavior,
            "name": config.name,
            "tools": tool_str,
            "parser_instructions": parser_instructions
        })
        return SystemMessage(content=content)

    def _serialize_tools(self, tools: dict[str, Tool], include_source: bool) -> str:
        return "".join(
            tool.to_instruction(include_source=include_source)
            for tool in tools.values()
        ).strip()
```

**Impact:**
- Single responsibility: Agent orchestrates, MessageBuilder builds messages
- Easier to test message construction
- More flexible for custom message formats

**Files to update:**
- Create `src/vindao_agents/builders/message_builder.py`
- Create `src/vindao_agents/builders/__init__.py`
- Update `Agent.__init__()` to use MessageBuilder
- Remove `Agent.__build_system_message()`

---

#### 2.3 Tool Loading Consistency
**Issue #8** | `Agent.py:215-222`

**Problem:**
- InferenceAdapter, ToolParser, AgentStore accept string OR instance
- Tools only accept string identifiers, always constructed internally
- Inconsistent API design

**Current patterns:**
| Component | Accepts String? | Accepts Instance? |
|-----------|----------------|-------------------|
| InferenceAdapter | ✅ | ✅ |
| ToolParser | ✅ | ✅ |
| AgentStore | ✅ | ✅ |
| Tools | ✅ | ❌ |

**Fix:**
```python
# Agent.__init__() - Accept Tool instances or strings
def __init__(
    self,
    ...
    tools: list[str | Tool] = [],  # ✓ Accept both
    ...
):
    self.tools = self.__load_tools(tools)

def __load_tools(self, tool_specs: list[str | Tool]) -> dict[str, Tool]:
    """Load tools from string identifiers or Tool instances."""
    loaded_tools = {}
    for spec in tool_specs:
        if isinstance(spec, Tool):
            # Direct tool instance
            loaded_tools[spec.name] = spec
        else:
            # String identifier - load functions
            loaded_functions = load_public_functions_from_identifier(spec)
            for name, f in loaded_functions:
                loaded_tools[name] = Tool(f)
    return loaded_tools
```

**Impact:**
- Consistent API across all components
- Users can pass pre-configured Tool instances
- More flexible for testing

**Files to update:**
- Update `Agent.__init__()` signature
- Update `Agent.__load_tools()`
- Update type hints in `AgentConfig`

---

#### 2.4 Parser Initialization Order
**Issue #9** | `Agent.py:64-71`

**Problem:**
- Comment says parser must be initialized early for system message building
- This creates unnecessary coupling between components
- Parser is only needed when building system message, not for loading tools

**Current code:**
```python
# Initialize parser early since it's needed for building the system message
if isinstance(parser, str):
    parser = parsers.get(parser, AtSyntaxParser)
self.parser = parser()
self.tools = self.__load_tools(tools)
```

**Fix:**
With MessageBuilder (2.2), this ordering requirement disappears:

```python
# No special ordering needed - MessageBuilder handles dependencies
self.tools = self.__load_tools(tools)
if isinstance(parser, str):
    parser = parsers.get(parser, AtSyntaxParser)
self.parser = parser()
```

**Impact:**
- Removes unnecessary coupling
- Cleaner initialization logic
- More maintainable

**Dependencies:** Should be done after 2.2 (MessageBuilder)

**Files to update:**
- Update `Agent.__init__()` - reorder initialization
- Remove misleading comment

---

### Phase 3: Optional Enhancements (1-2 weeks)

These are valuable but not critical:

#### 3.1 Add ToolRegistry
**Issue #6a** | Framework-wide

**Problem:**
- Tools stored as plain `dict[str, Tool]`
- No conflict detection (later tools silently override earlier ones)
- No validation before registration
- No lifecycle management

**Fix:**
```python
# Create: src/vindao_agents/registries/tool_registry.py
class ToolRegistry:
    """Manages tool registration with validation and conflict detection."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool, allow_override: bool = False) -> None:
        """Register a tool with conflict detection."""
        if tool.name in self._tools and not allow_override:
            raise ValueError(
                f"Tool '{tool.name}' already registered. "
                f"Use allow_override=True to replace it."
            )
        self._validate_tool(tool)
        self._tools[tool.name] = tool

    def _validate_tool(self, tool: Tool) -> None:
        """Validate tool before registration."""
        if not tool.name:
            raise ValueError("Tool must have a name")
        if not callable(tool.function):
            raise ValueError("Tool function must be callable")

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
```

**Impact:**
- Explicit error messages for tool conflicts
- Validation prevents invalid tools
- Better debugging experience

**Files to update:**
- Create `src/vindao_agents/registries/tool_registry.py`
- Create `src/vindao_agents/registries/__init__.py`
- Update `Agent.__load_tools()` to use ToolRegistry
- Update `Agent.tools` to be ToolRegistry instance

---

#### 3.2 Add ValidationLayer
**Issue #6b** | `executors/execute_tool_call.py`

**Problem:**
- Tool calls executed without validation
- No schema checking before execution
- No parameter type validation
- Runtime errors instead of early validation errors

**Fix:**
```python
# Create: src/vindao_agents/validation/tool_validator.py
class ToolValidator:
    """Validates tool calls before execution."""

    def validate_call(self, tool: Tool, call_args: dict) -> tuple[bool, str]:
        """
        Validate a tool call against the tool's signature.
        Returns (is_valid, error_message)
        """
        try:
            # Check required parameters
            sig = inspect.signature(tool.function)
            for param_name, param in sig.parameters.items():
                if param.default is inspect.Parameter.empty:
                    if param_name not in call_args:
                        return False, f"Missing required parameter: {param_name}"

            # Check parameter types if annotated
            for param_name, value in call_args.items():
                if param_name not in sig.parameters:
                    return False, f"Unknown parameter: {param_name}"

                param = sig.parameters[param_name]
                if param.annotation is not inspect.Parameter.empty:
                    if not isinstance(value, param.annotation):
                        return False, f"Parameter {param_name} expects {param.annotation}, got {type(value)}"

            return True, ""
        except Exception as e:
            return False, f"Validation error: {str(e)}"

# Update: executors/execute_tool_call.py
validator = ToolValidator()

def execute_tool_call(call: str, tool: Tool) -> Any:
    args = parse_call_args(call)

    # Validate before execution
    is_valid, error_msg = validator.validate_call(tool, args)
    if not is_valid:
        raise ValueError(f"Invalid tool call: {error_msg}")

    return tool.function(**args)
```

**Impact:**
- Better error messages before execution
- Prevents runtime errors from invalid calls
- Type safety for tool parameters

**Files to update:**
- Create `src/vindao_agents/validation/tool_validator.py`
- Create `src/vindao_agents/validation/__init__.py`
- Update `executors/execute_tool_call.py`

---

#### 3.3 Add Observability
**Issue #15** | Framework-wide

**Problem:**
- No token usage tracking
- No latency metrics
- No cost estimation
- No tool execution statistics
- Cannot optimize or debug performance

**Fix:**
```python
# Create: src/vindao_agents/observability/metrics.py
from dataclasses import dataclass, field
from time import time
from typing import Dict

@dataclass
class AgentMetrics:
    """Tracks agent execution metrics."""

    # Token usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    # Timing
    start_time: float = field(default_factory=time)
    end_time: float | None = None

    # Tool usage
    tool_calls: Dict[str, int] = field(default_factory=dict)
    tool_errors: Dict[str, int] = field(default_factory=dict)

    # Iterations
    total_iterations: int = 0

    def record_tool_call(self, tool_name: str, success: bool = True):
        if success:
            self.tool_calls[tool_name] = self.tool_calls.get(tool_name, 0) + 1
        else:
            self.tool_errors[tool_name] = self.tool_errors.get(tool_name, 0) + 1

    def record_tokens(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def finalize(self):
        self.end_time = time()

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or time()
        return end - self.start_time

    def to_dict(self) -> dict:
        return {
            "tokens": {
                "input": self.total_input_tokens,
                "output": self.total_output_tokens,
                "total": self.total_input_tokens + self.total_output_tokens
            },
            "timing": {
                "duration_seconds": self.duration_seconds
            },
            "tools": {
                "calls": self.tool_calls,
                "errors": self.tool_errors
            },
            "iterations": self.total_iterations
        }

# Add to Agent class
class Agent:
    def __init__(self, ..., enable_metrics: bool = False):
        ...
        self.metrics = AgentMetrics() if enable_metrics else None

    def get_metrics(self) -> dict:
        """Get execution metrics."""
        if not self.metrics:
            raise ValueError("Metrics not enabled. Set enable_metrics=True")
        return self.metrics.to_dict()
```

**Impact:**
- Performance insights
- Cost tracking
- Debugging support
- Usage analytics

**Dependencies:** Requires Phase 1.2 (Logging Framework)

**Files to update:**
- Create `src/vindao_agents/observability/metrics.py`
- Create `src/vindao_agents/observability/__init__.py`
- Update `Agent` class to track metrics
- Update `InferenceAdapter` to report token usage
- Update `execute_tool_call` to report tool metrics

---

## 📋 IMPLEMENTATION ORDER

### Week 1: Foundation
1. Day 1-2: Phase 1.1 (Path resolution) + Phase 1.2 (Logging)
2. Day 3-4: Phase 2.1 (Agent I/O extraction)
3. Day 5: Phase 2.2 (MessageBuilder)

### Week 2: Core Refactoring
4. Day 1: Phase 2.3 (Tool loading consistency)
5. Day 1: Phase 2.4 (Parser initialization order)
6. Day 2-3: Testing and bug fixes
7. Day 4-5: Documentation updates

### Week 3+: Optional Enhancements
8. Phase 3.1: ToolRegistry (if needed)
9. Phase 3.2: ValidationLayer (if needed)
10. Phase 3.3: Observability (if needed)

---

## 🎯 SUCCESS CRITERIA

### Code Quality
- ✅ All 64 tests continue passing
- ✅ Agent class reduced to < 150 lines (currently 234 lines)
- ✅ No print statements in core framework
- ✅ Consistent API patterns across all components

### Architecture
- ✅ Agent can be used in non-console environments
- ✅ Clear separation of concerns
- ✅ Path resolution centralized
- ✅ Message building extracted

### User Experience
- ✅ Backward compatibility maintained where possible
- ✅ Migration guide for breaking changes
- ✅ Updated examples and documentation
- ✅ Clear upgrade path

---

## 🚫 OUT OF SCOPE

The following are explicitly not being addressed:

1. **Async/await support** - Not needed for current use cases
2. **Session recovery** - Future enhancement, not critical
3. **Message role mutation** - Intentional design for model-agnostic tool calling
4. **Registry pattern** - Intentional for user extensibility
5. **Package naming** - Intentional design pattern

---

## 📊 CURRENT STATE

**Test Suite:** 79 tests passing, 0 failing (64 original + 15 new path resolution tests)
**Code Quality:** Priority 1 issues resolved, Phase 1.1 completed
**Next Step:** Begin Phase 1.2 (Logging Framework)

---

*Generated 2025-12-16*
