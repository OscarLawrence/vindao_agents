# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-16

### Added
- Initial release of Vindao Agents framework
- Core agent orchestration system
- Tool integration system (bash, file operations)
- Interactive CLI interface with `agent` command
- Session management and persistence
- Multiple predefined agents (DefaultAgent, Developer, SoftwareArchitect, CodeInspector)
- Support for multiple LLM providers via LiteLLM (OpenAI, Anthropic, Ollama, etc.)
- Streaming responses with rich formatting
- Markdown-based agent configuration
- Custom tool parser system
- JSON-based agent storage
- Comprehensive test suite
- PyPI packaging and distribution setup
- GitHub Actions CI/CD workflows
- Custom license with commercial profit-sharing

### Features
- Load agents from markdown files with YAML frontmatter
- Resume previous chat sessions by session ID
- List available predefined agents via CLI
- Extensible architecture for custom inference adapters, tool parsers, and storage backends
- Rich console output with formatting
- Environment variable configuration support

[Unreleased]: https://github.com/vindao/vindao_agents/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vindao/vindao_agents/releases/tag/v0.1.0
