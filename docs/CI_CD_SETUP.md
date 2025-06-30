# CI/CD Pipeline Documentation

This document describes the comprehensive CI/CD pipeline for the gpt-subtrans project, which ensures that the package maintains its installability via pipx and prevents packaging regressions.

## Overview

The CI/CD pipeline consists of several components:

1. **GitHub Actions Workflows** - Automated testing on multiple platforms and Python versions
2. **Pre-commit Hooks** - Local code quality checks before commits
3. **pipx Installation Tests** - Dedicated tests for package installation validation
4. **Local Test Runner** - Script for developers to test locally

## GitHub Actions Workflows

### Main CI Pipeline (`.github/workflows/ci.yml`)

The main CI pipeline runs on:
- **Triggers**: Push to `main`/`develop` branches, Pull Requests to `main`
- **Operating Systems**: Ubuntu, macOS, Windows
- **Python Versions**: 3.10, 3.11, 3.12, 3.13

#### Jobs

1. **test**: Runs the existing unit test suite
   - Installs dependencies with pip caching
   - Runs pytest with coverage reporting
   - Uploads coverage to Codecov (Ubuntu + Python 3.12 only)

2. **pipx-installation-test**: Validates pipx installation
   - Installs package using `pipx install .`
   - Verifies all 8 CLI tools are available in PATH
   - Tests help commands for each CLI tool
   - Validates basic SRT file parsing

3. **lint**: Code quality checks
   - Ruff linting and formatting (replaces black, isort, flake8)
   - Fast and comprehensive Python code analysis

4. **security**: Security scanning
   - bandit security analysis
   - safety dependency vulnerability check

## pipx Installation Tests

### Test File: `tests/test_pipx_installation.py`

This dedicated test file contains comprehensive tests for:

#### TestPipxInstallation Class
- `test_cli_tools_in_path()`: Verifies all 8 CLI tools are in PATH
- `test_cli_help_commands()`: Tests help output for each tool
- `test_package_data_installation()`: Validates instructions.txt installation
- `test_srt_file_parsing()`: Tests basic SRT parsing without API calls
- `test_provider_loading()`: Verifies translation providers load correctly
- `test_different_cli_variants()`: Tests tool-specific help text

#### TestPackageStructure Class
- `test_pyproject_toml_entry_points()`: Validates entry points in pyproject.toml
- `test_src_layout_structure()`: Checks src layout compliance
- `test_instructions_file_exists()`: Verifies package data files

### Expected CLI Tools

The tests validate these 8 entry points:
- `gpt-subtrans`
- `claude-subtrans`
- `gemini-subtrans`
- `deepseek-subtrans`
- `mistral-subtrans`
- `bedrock-subtrans`
- `llm-subtrans`
- `azure-subtrans`

## Pre-commit Hooks

### Configuration: `.pre-commit-config.yaml`

Pre-commit hooks run automatically before commits and include:

#### Code Quality
- **Ruff**: Fast Python linter and formatter (replaces black, isort, flake8)
  - Linting with comprehensive rule set
  - Code formatting with Black-compatible style
  - Import sorting with isort-compatible behavior
  - Configured in pyproject.toml

#### Security & General
- **bandit**: Security vulnerability scanning
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml/toml/json**: Validate file formats
- **check-merge-conflict**: Detect merge conflict markers
- **debug-statements**: Detect debug statements

#### pipx Installation Test
- **pipx-installation-test**: Runs package structure tests on pre-push

### Setup Pre-commit

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Install pre-push hooks
pre-commit install --hook-type pre-push

# Run all hooks manually
pre-commit run --all-files
```

## Local Development

### Test Runner Script: `scripts/test_pipx_installation.py`

A comprehensive local test runner that developers can use:

```bash
# Run all pipx installation tests
python scripts/test_pipx_installation.py

# Run quietly (less verbose output)
python scripts/test_pipx_installation.py --quiet
```

The script provides:
- Colored terminal output
- Detailed error reporting
- Step-by-step test execution
- Summary of results

### Running Tests Locally

```bash
# Run all tests
pytest

# Run only pipx installation tests
pytest tests/test_pipx_installation.py -v

# Run only package structure tests (fast)
pytest tests/test_pipx_installation.py::TestPackageStructure -v

# Run with coverage
pytest --cov=src/PySubtitle --cov-report=html
```

## Branch Protection

To ensure the CI/CD pipeline is effective, configure branch protection rules:

### Recommended Settings for `main` branch:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Required status checks:
  - `test (ubuntu-latest, 3.12)`
  - `pipx-installation-test (ubuntu-latest, 3.12)`
  - `lint`
  - `security`
- ✅ Require pull request reviews before merging
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Restrict pushes that create files larger than 100MB

## Troubleshooting

### Common Issues

1. **pipx not found in CI**
   - The workflow installs pipx automatically
   - PATH is configured for each OS

2. **CLI tools not in PATH**
   - Check pyproject.toml entry points
   - Verify pipx installation succeeded
   - Check PATH configuration

3. **Package data not found**
   - Verify `[tool.setuptools.package-data]` in pyproject.toml
   - Check that files exist in src/PySubtitle/instructions/

4. **Tests timeout**
   - Default timeout is 30 seconds
   - Increase if needed for slower systems

### Debugging Failed Tests

```bash
# Run with maximum verbosity
pytest tests/test_pipx_installation.py -v -s

# Run specific test
pytest tests/test_pipx_installation.py::TestPipxInstallation::test_cli_tools_in_path -v

# Check pipx installation manually
pipx install . --force
pipx list
```

## Maintenance

### Updating Dependencies

1. Update pre-commit hook versions in `.pre-commit-config.yaml`
2. Update GitHub Actions versions in `.github/workflows/ci.yml`
3. Test locally before committing

### Adding New CLI Tools

1. Add entry point to `pyproject.toml`
2. Update `EXPECTED_CLI_TOOLS` in test files
3. Add tool-specific tests if needed

### Python Version Updates

1. Update matrix in GitHub Actions workflow
2. Test locally with new Python version
3. Update documentation

## Quick Commands

Use the provided Makefile for common development tasks:

```bash
# Install development dependencies
make install-dev

# Run all tests
make test

# Run pipx installation tests
make test-pipx

# Run code quality checks
make lint

# Format code
make format

# Run security checks
make security

# Clean up build artifacts
make clean

# Install package locally with pipx
make install-local

# Full CI simulation
make ci
```
