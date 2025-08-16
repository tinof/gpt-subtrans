# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- `make test` - Run all tests (unit + pipx installation tests)
- `make test-unit` - Run unit tests only (excludes pipx tests)
- `make test-pipx` - Run pipx installation tests specifically
- `python -m pytest tests/ -v` - Direct pytest execution
- `python -m pytest tests/ -v -k "not test_pipx_installation"` - Unit tests only

### Code Quality
- `make lint` - Run Ruff linting on src/ and tests/
- `make format` - Format code with Ruff
- `make format-check` - Check code formatting without changes
- `make security` - Run Bandit security analysis
- `make ci` - Run full CI simulation (format-check, lint, security, test-unit, test-pipx)

### Development Setup
- `make install-dev` - Install development dependencies and pre-commit hooks
- `make install-local` - Install package locally with pipx
- `pip install -e .` - Install in development mode
- `pip install -e .[all]` - Install with all provider dependencies

### Build and Clean
- `make clean` - Remove build artifacts, cache files, and temporary files
- `python -m build` - Build distribution packages

## Architecture Overview

### Core Structure
This is a command-line subtitle translation tool using various LLM providers. The architecture follows a provider-based pattern where each AI service (OpenAI, Claude, Gemini, etc.) has its own implementation.

### Key Components

**Translation Flow:**
1. `SubtitleFile` - Parses and manages SRT subtitle files
2. `SubtitleBatcher` - Divides subtitles into batches for efficient translation
3. `SubtitleTranslator` - Orchestrates the translation process
4. `TranslationProvider` - Abstract base for AI service providers
5. `TranslationClient` - Handles communication with AI APIs

**Provider System:**
- Each provider in `src/PySubtitle/Providers/` implements the base `TranslationProvider`
- Provider-specific clients handle API communication
- CLI entry points in `src/PySubtitle/cli/` for each provider

**Entry Points:**
- `gpt-subtrans` (OpenAI GPT)
- `claude-subtrans` (Anthropic Claude)
- `gemini-subtrans` (Google Gemini)
- `deepseek-subtrans` (DeepSeek)
- `mistral-subtrans` (Mistral AI)
- `azure-subtrans` (Azure OpenAI)
- `bedrock-subtrans` (Amazon Bedrock)
- `llm-subtrans` (Custom LLM servers)

### Code Style Standards
- **Naming**: PascalCase for classes/methods, snake_case for variables
- **Type hints**: Required for parameters, return values, class variables
- **Threading**: Uses locks (RLock) for thread-safe operations
- **Error handling**: Custom exceptions with specific error types
- **Line length**: 127 characters (Ruff configuration)

### Project Structure
- `src/PySubtitle/` - Main package code
- `tests/` - Unit and integration tests
- `scripts/` - Utility scripts (pipx installation testing)
- Configuration files: `pyproject.toml`, `pytest.ini`, `Makefile`

### Testing Strategy
- Unit tests for core functionality
- Integration tests for pipx installation
- Security scanning with Bandit
- Code quality checks with Ruff
- Pre-commit hooks for code formatting and linting

### Provider Dependencies
Each AI provider requires specific SDK installation via `pipx inject` or pip optional dependencies:
- OpenAI: `openai`
- Claude: `anthropic`
- Gemini: `google-genai`, `google-api-core`
- Mistral: `mistralai`
- Bedrock: `boto3`
- DeepSeek: `openai` (uses OpenAI SDK)
