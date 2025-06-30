# Development Guide

This guide covers development setup, testing, and contribution guidelines for the gpt-subtrans project.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/machinewrapped/gpt-subtrans.git
cd gpt-subtrans

# Install development dependencies
make install-dev

# Install package in development mode
pip install -e .

# Run tests
make test

# Test pipx installation
make test-pipx
```

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- pipx (for installation testing)
- Git

### Installation

1. **Install development dependencies:**
   ```bash
   make install-dev
   ```
   This installs pytest, linting tools, pre-commit hooks, and other development dependencies.

2. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```
   This allows you to import and test the package while developing.

3. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   pre-commit install --hook-type pre-push
   ```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit          # Unit tests only
make test-pipx          # pipx installation tests

# Run tests with coverage
pytest --cov=src/PySubtitle --cov-report=html

# Run specific test file
pytest tests/test_Subtitles.py -v
```

### Test Categories

1. **Unit Tests** (`tests/test_*.py`): Test individual components and functions
2. **Integration Tests** (`tests/test_ChineseDinner.py`, `tests/test_Translator.py`): Test component interactions
3. **pipx Installation Tests** (`tests/test_pipx_installation.py`): Validate package installation and CLI tools

### pipx Installation Testing

The project includes comprehensive tests to ensure the package installs correctly via pipx:

```bash
# Run the local test runner (recommended)
python scripts/test_pipx_installation.py

# Run pytest version
pytest tests/test_pipx_installation.py -v

# Test only package structure (fast)
pytest tests/test_pipx_installation.py::TestPackageStructure -v
```

## Code Quality

### Linting and Formatting

```bash
# Run all code quality checks with Ruff
make lint

# Format code automatically with Ruff
make format

# Check formatting without making changes
make format-check

# Run security checks
make security
```

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit:

- **Ruff**: Fast Python linter and formatter (replaces black, isort, flake8)
- **bandit**: Security scanning
- **General file checks**: YAML, TOML, JSON validation, trailing whitespace, etc.

To run hooks manually:
```bash
pre-commit run --all-files
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **Main CI Pipeline** (`.github/workflows/ci.yml`):
   - Runs on push to main/develop and PRs to main
   - Tests on Ubuntu, macOS, Windows
   - Python versions: 3.10, 3.11, 3.12, 3.13
   - Includes unit tests, linting, security scans

2. **pipx Validation** (`.github/workflows/pipx-validation.yml`):
   - Runs on PRs that modify source code or packaging
   - Validates pipx installation across platforms
   - Tests all CLI entry points
   - Verifies SRT file parsing

### Branch Protection

The `main` branch should be protected with these requirements:
- All status checks must pass
- Require up-to-date branches
- Require pull request reviews

## Making Changes

### Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test:**
   ```bash
   # Make changes
   # ...

   # Test your changes
   make test
   make test-pipx
   make lint
   ```

3. **Commit with pre-commit hooks:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

4. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Adding New CLI Tools

If you add a new CLI entry point:

1. **Update `pyproject.toml`:**
   ```toml
   [project.scripts]
   your-new-tool = "PySubtitle.cli:your_main_function"
   ```

2. **Update test expectations:**
   - Add the tool name to `EXPECTED_CLI_TOOLS` in `tests/test_pipx_installation.py`
   - Add tool-specific tests if needed

3. **Test the changes:**
   ```bash
   make test-pipx
   ```

### Modifying Package Structure

If you change the package structure:

1. **Update imports** in test files if needed
2. **Update `pyproject.toml`** if package data changes
3. **Run structure tests:**
   ```bash
   pytest tests/test_pipx_installation.py::TestPackageStructure -v
   ```

## Debugging

### Common Issues

1. **Import errors in tests:**
   ```bash
   # Install package in development mode
   pip install -e .
   ```

2. **pipx installation fails:**
   ```bash
   # Check package structure
   python scripts/test_pipx_installation.py

   # Reinstall with force
   pipx install . --force
   ```

3. **Pre-commit hooks fail:**
   ```bash
   # Fix formatting issues
   make format

   # Run hooks manually
   pre-commit run --all-files
   ```

### Verbose Testing

```bash
# Run tests with maximum verbosity
pytest tests/ -v -s

# Debug specific test
pytest tests/test_pipx_installation.py::TestPipxInstallation::test_cli_tools_in_path -v -s

# Run with pdb debugger
pytest tests/test_Subtitles.py --pdb
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Run full test suite:**
   ```bash
   make ci
   ```
3. **Create release PR** to main branch
4. **Tag release** after merge
5. **Publish to PyPI** (if applicable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all CI checks pass
5. Submit a pull request

For detailed CI/CD documentation, see [CI_CD_SETUP.md](CI_CD_SETUP.md).
