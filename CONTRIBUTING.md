# Contributing to portfolio-media

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Setting Up Development Environment

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/user/portfolio-media.git
   cd portfolio-media
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Making Changes

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following existing code style

3. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   ```

4. **Run linting and formatting**:
   ```bash
   ruff check .
   ruff format .
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   ```

### Code Style

This project uses:
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

Run all quality checks:
```bash
ruff check . && ruff format . && mypy . && pytest
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names that follow the pattern `test_<function>_<scenario>`
- Include docstrings for complex test logic

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_specific.py
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if your changes affect usage
2. **Add tests** for new functionality or bug fixes
3. **Ensure all tests pass** before submitting
4. **Create a pull request** with:
   - Clear description of changes
   - Reference to related issues (if any)
   - Screenshots for UI changes (if applicable)

### Pull Request Guidelines

- Keep PRs focused on a single issue or feature
- Write clear commit messages
- Respond to review feedback promptly
- Ensure CI checks pass before requesting review

## Getting Help

- **Documentation**: Check the README and docs/ directory
- **Issues**: Search existing GitHub issues first
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
