# Contributing to gst

Thank you for your interest in contributing to `gst`! This guide will help you get started with development.

## Development Setup

To contribute to this project:

1. Clone the repository
2. Run the development setup script:
   ```bash
   ./scripts/setup_dev.sh
   ```

This script installs development dependencies (ruff, mypy, pytest, build, twine, pytest) and sets up a pre-commit hook that automatically runs:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Unit tests (pytest)

## Running Tests

```bash
pytest tests/                    # Run all tests
pytest tests/test_gst.py -v      # Run specific test file with verbose output
```

### Test Types

- **Unit tests** (`tests/test_gst.py`): Mock-based tests for individual functions
- **Integration tests** (`tests/test_git_integration.py`): Tests using real git repositories

## Code Quality

The project uses several tools to maintain code quality:

### Pre-commit Hook

The pre-commit hook automatically runs on every commit:
1. **ruff format** - Code formatting
2. **ruff check --fix** - Linting with auto-fixes
3. **mypy** - Type checking
4. **pytest** - Full test suite

### Manual Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check --fix .

# Type checking
mypy gst.py

# Run tests with coverage
pytest tests/ --cov=gst --cov-report=html
```

## Documentation

### Regenerating README images

```bash
python scripts/generate_svg_examples.py
```

### Code Documentation

- Use type hints for all functions
- Write docstrings for public functions
- Keep comments concise and focused on "why" not "what"

## Development Guidelines

### Code Style

- Follow PEP 8 (enforced by ruff)
- Use 2-space indentation (configured in pyproject.toml)
- Maximum line length: 88 characters
- Use descriptive variable names

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use integration tests for git operations
- Use unit tests with mocks for isolated functionality

### Git Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Ensure all tests pass: `pytest`
5. Commit your changes (pre-commit hook will run)
6. Push to your fork: `git push origin feature-name`
7. Create a pull request

## Project Structure

```
gst-python/
├── gst.py                      # Main application code
├── tests/
│   ├── test_gst.py            # Unit tests
│   └── test_git_integration.py # Integration tests
├── scripts/
│   ├── setup_dev.sh           # Development setup script
│   └── generate_svg_examples.py # README image generation
├── hooks/
│   └── pre-commit             # Git pre-commit hook
└── docs/
    └── images/                # README demonstration images
```

## Compatibility

The project supports:
- **Python 3.8+** (fully tested and supported)
- **Python 3.6, 3.7** (best-effort support with manual testing)
- **Git version >=2**
- **Platforms**: Linux, Mac, Windows

## Release Process

1. Update version in `pyproject.toml` and `setup.cfg`
2. Run `./scripts/update_pypi.sh` to publish to PyPI
3. Create a git tag for the release
4. Update CHANGELOG.md

## Getting Help

- Check existing issues and pull requests
- Create a new issue for bugs or feature requests
- Join discussions in existing issues
- Review the codebase and tests for examples

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and contribute
- Follow the project's established patterns

Thank you for contributing to `gst`!