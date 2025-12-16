# Test Suite Refactoring Plan

## Executive Summary

This document outlines a systematic plan to refactor and enhance the vindao_agents test suite from its current state (6.5/10) to production-ready (9+/10). The plan is organized by priority and logical implementation order to minimize disruption and maximize value delivery.

**Current State**: Good foundation with critical gaps
**Target State**: Comprehensive, maintainable, production-ready test suite
**Estimated Effort**: 3-4 weeks (1 developer)

---

## Phase 1: Critical Foundations (Week 1)

**Goal**: Fix critical gaps and establish testing infrastructure
**Priority**: CRITICAL - Blocks production deployment

### 1.1 Complete Missing Core Tests (Days 1-3)

**Rationale**: These are the most critical functions with zero test coverage

#### Task 1.1.1: Implement TestAgentInvoke

- **File**: `tests/test_agent.py`
- **Priority**: P0 - CRITICAL
- **Tests to Add**: 9 tests covering:
  - Simple responses without tools
  - Reasoning content handling
  - Tool call detection and execution
  - Tool result processing
  - Disable tool call marker
  - Multiple iteration cycles
  - Max iteration warnings
  - Empty/malformed responses
- **Coverage Target**: >90% of invoke method

#### Task 1.1.2: Implement TestAgentSave

- **File**: `tests/test_agent.py`
- **Priority**: P0 - CRITICAL
- **Tests to Add**: 8 tests covering:
  - Session file creation
  - Custom save paths
  - State preservation
  - Directory creation
  - File overwriting
  - Auto-save behavior
  - Manual save
  - Permission errors
- **Coverage Target**: >95% of save method

---

### 1.2 Consolidate Test Infrastructure (Days 4-5)

**Rationale**: Eliminate duplication, improve maintainability before adding more tests

#### Task 1.2.1: Enhance conftest.py

- **File**: `tests/conftest.py`
- **Priority**: P0 - CRITICAL
- **Changes**:
  - Move `MockInferenceAdapter` from test_agent.py to conftest.py
  - Add fixtures for common tool collections
  - Add fixtures for message sequences
  - Add fixtures for agent configurations
  - Add fixtures for file-based test data
  - Add specialized mock adapters (with reasoning, with tool calls, etc.)
- **Impact**: Reduce code duplication by ~200 lines

#### Task 1.2.2: Update pyproject.toml

- **File**: `pyproject.toml`
- **Priority**: P0 - CRITICAL
- **Changes**:
  - Add test markers (unit, integration, slow, network)
  - Configure coverage thresholds (80% minimum)
  - Add coverage exclusions
  - Configure pytest addopts (verbose, strict-markers, etc.)
  - Add timeout settings
  - Configure warning filters
- **Impact**: Enforce quality standards automatically

#### Task 1.2.3: Refactor Existing Tests

- **Files**: All test files using MockInferenceAdapter
- **Priority**: P1 - HIGH
- **Changes**:
  - Replace inline mocks with conftest fixtures
  - Add appropriate test markers
  - Remove duplicate setup code
- **Impact**: Cleaner, more maintainable tests

---

### 1.3 Add Critical Error Handling Tests (Day 5)

**Rationale**: Production systems must handle failures gracefully

#### Task 1.3.1: Network and API Error Tests

- **File**: `tests/test_agent_error_handling.py` (NEW)
- **Priority**: P0 - CRITICAL
- **Tests to Add**: 10+ tests covering:
  - Connection errors during invoke
  - API timeout errors
  - Rate limiting errors
  - Retry mechanism validation
  - Exponential backoff behavior
  - Maximum retry exhaustion
  - Partial response handling
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.network`

#### Task 1.3.2: Tool Execution Error Tests

- **File**: `tests/test_tool_error_handling.py` (NEW)
- **Priority**: P0 - CRITICAL
- **Tests to Add**: 8+ tests covering:
  - Tool not found errors
  - Tool execution exceptions
  - Tool timeout errors
  - Malformed tool call syntax
  - Invalid tool arguments
  - Tool call parsing edge cases
  - Circular tool dependencies
- **Markers**: `@pytest.mark.unit`

#### Task 1.3.3: File I/O Error Tests

- **File**: `tests/test_file_error_handling.py` (NEW)
- **Priority**: P1 - HIGH
- **Tests to Add**: 6+ tests covering:
  - Permission denied on save
  - Disk full errors
  - Corrupted session files
  - Missing parent directories
  - File locking conflicts
  - Invalid JSON in session files
- **Markers**: `@pytest.mark.unit`

---

## Phase 2: Integration & Contract Testing (Week 2)

**Goal**: Test component interactions and interface contracts
**Priority**: HIGH - Needed for confidence in production

### 2.1 Add Integration Tests (Days 6-8)

**Rationale**: Unit tests alone don't catch integration issues

#### Task 2.1.1: End-to-End Conversation Tests

- **File**: `tests/integration/test_conversation_flows.py` (NEW)
- **Priority**: P1 - HIGH
- **Tests to Add**: 5+ scenarios:
  - Simple question-answer flow
  - Multi-turn conversation with context
  - Tool call during conversation
  - Error recovery during conversation
  - Session persistence and reload
- **Markers**: `@pytest.mark.integration`, `@pytest.mark.slow`
- **Note**: Use recorded LLM responses (VCR pattern)

#### Task 2.1.2: Tool Integration Tests

- **File**: `tests/integration/test_tool_integration.py` (NEW)
- **Priority**: P1 - HIGH
- **Tests to Add**: 6+ scenarios:
  - Agent → Tool → File system interaction
  - Tool chain execution (tool calling another tool)
  - Mixed success/failure tool calls
  - Tool state persistence
  - Tool with side effects
  - Tool requiring external resources
- **Markers**: `@pytest.mark.integration`

#### Task 2.1.3: Adapter Integration Tests

- **File**: `tests/integration/test_adapter_integration.py` (NEW)
- **Priority**: P1 - HIGH
- **Tests to Add**: 4+ scenarios per adapter:
  - Real API call with recorded response
  - Message format compatibility
  - Streaming behavior
  - Error response handling
- **Markers**: `@pytest.mark.integration`, `@pytest.mark.network`
- **Note**: Use environment variables to enable/disable real API tests

---

### 2.2 Add Contract Tests (Days 9-10)

**Rationale**: Ensure interface compliance without implementation coupling

#### Task 2.2.1: Adapter Interface Contract Tests

- **File**: `tests/contracts/test_adapter_contracts.py` (NEW)
- **Priority**: P1 - HIGH
- **Tests to Add**: Contract suite covering:
  - Required methods exist
  - Method signatures match interface
  - Return types are correct
  - Error types are consistent
  - Streaming behavior is standard
- **Apply to**: All adapter implementations
- **Pattern**: Parametrized tests across all adapters

#### Task 2.2.2: Tool Interface Contract Tests

- **File**: `tests/contracts/test_tool_contracts.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: Contract suite covering:
  - Tool metadata extraction
  - Signature parsing
  - Docstring format
  - Return value serialization
  - Exception handling format
- **Apply to**: All tool implementations

#### Task 2.2.3: Message Format Contract Tests

- **File**: `tests/contracts/test_message_contracts.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: Contract suite covering:
  - Serialization/deserialization round-trips
  - Required fields validation
  - Type validation
  - Timestamp handling
  - Message ordering guarantees
- **Apply to**: All message types

---

## Phase 3: Edge Cases & Property Testing (Week 3)

**Goal**: Harden against unexpected inputs and conditions
**Priority**: MEDIUM - Improves robustness

### 3.1 Add Edge Case Tests (Days 11-13)

**Rationale**: Real-world inputs are messy and unpredictable

#### Task 3.1.1: Input Validation Edge Cases

- **File**: `tests/edge_cases/test_input_validation.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: 15+ tests covering:
  - Empty strings in all fields
  - None values where strings expected
  - Extremely long messages (>100k chars)
  - Unicode and emoji handling
  - Special characters in tool names
  - Whitespace-only inputs
  - Control characters in content
  - Invalid UTF-8 sequences
  - Mixed encodings
  - Binary data in text fields
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.edge_case`

#### Task 3.1.2: State Management Edge Cases

- **File**: `tests/edge_cases/test_state_edge_cases.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: 10+ tests covering:
  - Empty message history
  - Extremely large message history (10k+ messages)
  - Concurrent state modifications
  - Session ID collisions
  - Timestamp edge cases (past/future dates)
  - Rapid sequential state updates
  - State corruption recovery
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.edge_case`

#### Task 3.1.3: Tool Call Edge Cases

- **File**: `tests/edge_cases/test_tool_call_edge_cases.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: 12+ tests covering:
  - Nested function call syntax
  - Multiple tool calls in single message
  - Tool calls with multiline arguments
  - Tool calls with escaped characters
  - Tool calls with lambda expressions
  - Ambiguous tool call syntax
  - Tool calls in code blocks
  - Tool calls in quotes
  - Incomplete tool calls
  - Tool calls with kwargs
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.edge_case`

---

### 3.2 Add Property-Based Tests (Days 14-15)

**Rationale**: Find bugs through randomized, systematic exploration

#### Task 3.2.1: Setup Hypothesis

- **File**: `pyproject.toml`
- **Priority**: P2 - MEDIUM
- **Changes**:
  - Add hypothesis to dev dependencies
  - Configure hypothesis settings
  - Add hypothesis profile for CI
- **Note**: First property-based testing for this project

#### Task 3.2.2: Message Serialization Properties

- **File**: `tests/properties/test_message_properties.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Properties to Test**:
  - Round-trip serialization preserves data
  - Message order is preserved
  - Timestamps are monotonic
  - Type information is maintained
  - Invalid inputs raise appropriate errors
- **Strategy**: Generate random messages, test invariants

#### Task 3.2.3: Tool Call Parsing Properties

- **File**: `tests/properties/test_tool_parsing_properties.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Properties to Test**:
  - Valid calls always parse
  - Invalid calls always fail gracefully
  - Parsing is consistent (same input = same output)
  - Whitespace handling is consistent
  - Quoted strings preserve content
- **Strategy**: Generate random tool call strings

#### Task 3.2.4: State Management Properties

- **File**: `tests/properties/test_state_properties.py` (NEW)
- **Priority**: P3 - LOW
- **Properties to Test**:
  - Message count never decreases
  - Timestamps always increase
  - Session ID never changes
  - State transitions are valid
  - Concurrent operations maintain consistency
- **Strategy**: Generate random state operations sequences

---

## Phase 4: Performance & Specialized Testing (Week 4)

**Goal**: Ensure system performs under realistic conditions
**Priority**: MEDIUM-LOW - Optimization and special scenarios

### 4.1 Add Performance Tests (Days 16-17)

**Rationale**: Prevent performance regressions

#### Task 4.1.1: Throughput Tests

- **File**: `tests/performance/test_throughput.py` (NEW)
- **Priority**: P3 - LOW
- **Tests to Add**: 5+ benchmarks:
  - Messages per second processing
  - Tool calls per second execution
  - State save/load operations per second
  - Memory usage with varying message counts
  - Startup time measurement
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.performance`
- **Tools**: pytest-benchmark

#### Task 4.1.2: Load Tests

- **File**: `tests/performance/test_load.py` (NEW)
- **Priority**: P3 - LOW
- **Tests to Add**: 4+ scenarios:
  - Sustained load over time
  - Spike load handling
  - Memory leak detection
  - Resource cleanup verification
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.performance`

#### Task 4.1.3: Concurrency Tests

- **File**: `tests/performance/test_concurrency.py` (NEW)
- **Priority**: P3 - LOW
- **Tests to Add**: 6+ scenarios:
  - Multiple agents running simultaneously
  - Concurrent tool execution
  - Race conditions in state management
  - Thread safety of adapters
  - Session file locking
  - Deadlock detection
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.concurrency`

---

### 4.2 Add Regression Tests (Day 18)

**Rationale**: Prevent known bugs from reoccurring

#### Task 4.2.1: Create Regression Test Suite

- **File**: `tests/regression/test_known_issues.py` (NEW)
- **Priority**: P2 - MEDIUM
- **Tests to Add**: One test per known issue:
  - Issue #2: Error handling in read_files formats exception
  - Issue #10: Exception message appears twice
  - Any future reported bugs
- **Pattern**: Each test references issue number and description
- **Markers**: `@pytest.mark.regression`

---

### 4.3 Add Mutation Testing (Days 19-20)

**Rationale**: Verify test suite actually catches bugs

#### Task 4.3.1: Setup Mutation Testing

- **File**: `pyproject.toml`
- **Priority**: P3 - LOW
- **Changes**:
  - Add mutmut to dev dependencies
  - Configure mutation testing paths
  - Create mutation testing script
- **Target**: 90%+ mutation score

#### Task 4.3.2: Run Initial Mutation Analysis

- **Priority**: P3 - LOW
- **Activities**:
  - Run mutmut on core modules
  - Analyze surviving mutants
  - Add tests to kill surviving mutants
  - Document mutation testing process
- **Output**: Mutation testing report and improvement plan

---

## Phase 5: Documentation & CI/CD Integration (Week 4)

**Goal**: Make test suite usable and automated
**Priority**: HIGH - Essential for team adoption

### 5.1 Document Testing Strategy (Day 19)

#### Task 5.1.1: Update tests/README.md

- **File**: `tests/README.md`
- **Priority**: P1 - HIGH
- **Sections to Add/Update**:
  - Testing philosophy and principles
  - Test categories and markers
  - How to run different test suites
  - How to write new tests
  - Fixture usage guide
  - CI/CD integration details
  - Coverage expectations
  - Performance test interpretation

#### Task 5.1.2: Add Testing Guidelines

- **File**: `TESTING_GUIDELINES.md` (NEW)
- **Priority**: P1 - HIGH
- **Content**:
  - When to write unit vs integration tests
  - Mocking guidelines and best practices
  - Test naming conventions
  - Test organization principles
  - Code coverage philosophy
  - How to handle flaky tests
  - Performance testing guidelines

#### Task 5.1.3: Create Test Templates

- **File**: `tests/templates/` (NEW)
- **Priority**: P2 - MEDIUM
