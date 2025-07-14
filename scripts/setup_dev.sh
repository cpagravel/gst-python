#!/bin/bash

# Development setup script for gst-python
# This script installs development dependencies and sets up git hooks

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up development environment for gst-python..."

# Install development dependencies
echo "Installing development dependencies (black, mypy, ruff)..."
pip3 install black mypy ruff

# Configure local repository to use local hooks instead of global ones
echo "Configuring repository to use local git hooks..."
cd "$PROJECT_ROOT"
git config core.hooksPath .git/hooks

# Install pre-commit hook
echo "Installing pre-commit hook..."
cp "$PROJECT_ROOT/hooks/pre-commit" "$PROJECT_ROOT/.git/hooks/pre-commit"
chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"

echo "✓ Development setup complete!"
echo ""
echo "The pre-commit hook will now run on each commit:"
echo "  - black formatter"
echo "  - ruff linter (includes PEP8 naming conventions)"
echo "  - mypy type checker"
echo ""
echo "You can also run these tools manually:"
echo "  black *.py           # Format code"
echo "  ruff check *.py      # Lint code (PEP8, naming, etc.)"
echo "  mypy *.py            # Type check"