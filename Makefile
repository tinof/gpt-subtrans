.PHONY: help install-dev test test-pipx test-unit lint format security clean install-local ci

# Default target
help:
	@echo "Available commands:"
	@echo "  install-dev    Install development dependencies"
	@echo "  test          Run all tests"
	@echo "  test-pipx     Run pipx installation tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  lint          Run code quality checks with Ruff"
	@echo "  format        Format code with Ruff"
	@echo "  format-check  Check code formatting without making changes"
	@echo "  security      Run security checks"
	@echo "  clean         Clean up build artifacts"
	@echo "  install-local Install package locally with pipx"
	@echo "  ci            Run full CI simulation locally"

# Install development dependencies
install-dev:
	python -m pip install --upgrade pip
	python -m pip install pytest pytest-cov ruff bandit safety pre-commit
	pre-commit install
	pre-commit install --hook-type pre-push

# Run all tests
test:
	python -m pytest tests/ -v

# Run pipx installation tests specifically
test-pipx:
	python scripts/test_pipx_installation.py

# Run unit tests only (excluding pipx tests)
test-unit:
	python -m pytest tests/ -v -k "not test_pipx_installation"

# Run code quality checks
lint:
	ruff check src/ tests/

# Format code
format:
	ruff format src/ tests/

# Check formatting without making changes
format-check:
	ruff format src/ tests/ --check

# Run security checks
security:
	bandit -r src/ -f json -o bandit-report.json || true
	bandit -r src/

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -f bandit-report.json
	rm -f safety-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install package locally with pipx
install-local:
	pipx install . --force

# Run full CI simulation locally
ci: clean format-check lint security test-unit test-pipx
	@echo "✅ All CI checks passed locally!"
