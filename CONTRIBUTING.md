# Contributing to VaultRAG

Thank you for your interest in contributing to VaultRAG! We welcome bug reports, feature suggestions, and pull requests.

## Local Setup
Refer to the [README.md](README.md) for local environment setup, Ollama model downloads, and start commands.

## Code Standards
- **Typing**: Keep all Python code fully typed. Use `mypy` style annotations.
- **Imports**: Ensure all backend imports are relative (e.g. `from backend.retrieval...`) and don't contain hardcoded system paths.
- **Logging**: Use standard Python `logging` instead of raw `print` statements.

## Testing
Always run the test suite and verify that all tests pass before opening a pull request:
```bash
python -m pytest
```
