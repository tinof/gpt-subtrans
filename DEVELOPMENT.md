# GPT-SubTrans Development Guide

## Commands
- Run all tests: `python -m unittest discover tests`
- Run single test: `python -m unittest tests.test_MODULE`
- Build distribution: `python -m build`
- Install for development: `pip install -e .`
- Install with all providers: `pip install -e .[all]`

## Code Style
- **Naming**: PascalCase for classes and methods, snake_case for variables
- **Imports**: Standard lib → third-party → local, alphabetical within groups
- **Types**: Use type hints for parameters, return values, and class variables
- **Docstrings**: Triple-quoted concise descriptions for classes and methods
- **Error handling**: Custom exceptions, specific except blocks, input validation
- **Class structure**: Docstring → constants → init → properties → public methods → private methods
- **Threading safety**: Use locks (RLock/QRecursiveMutex) for thread-safe operations
- **Validation**: Validate inputs with helpful error messages
