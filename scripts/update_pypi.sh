#!/bin/bash

# =============================================================================
# PyPI Release Script for gst-python
# =============================================================================
# This script automates the process of building and releasing a new version
# of the gst package to PyPI using modern Python packaging (pyproject.toml).
#
# PREREQUISITES:
# 1. The script will automatically install required tools (build, twine)
#    Or run the development setup: ./scripts/setup_dev.sh
#
# 2. Configure PyPI authentication (choose one):
#    Option A: API Token (recommended)
#      - Go to https://pypi.org/manage/account/token/
#      - Create a new API token
#      - Store in ~/.pypirc:
#        [pypi]
#        username = __token__
#        password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#    
#    Option B: Username/Password
#      - Store credentials in ~/.pypirc:
#        [pypi]
#        username = your_username
#        password = your_password
#
# BEFORE RUNNING THIS SCRIPT:
# 1. Update the version number in both pyproject.toml and setup.cfg
# 2. Update CHANGELOG.md with release notes
# 3. Commit all changes to git
# 4. Test the package locally: pip install -e .
# 5. Run tests and linting: ruff check && mypy gst.py
#
# USAGE:
#   ./scripts/update_pypi.sh [--test-pypi]
#
# OPTIONS:
#   --test-pypi    Upload to TestPyPI instead of PyPI (for testing)
#
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
USE_TEST_PYPI=false
if [[ "$1" == "--test-pypi" ]]; then
    USE_TEST_PYPI=true
    log_info "Using TestPyPI for upload"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

log_info "Starting PyPI release process for gst-python..."

# Check if required tools are installed
if ! command -v python3 &> /dev/null; then
    log_error "Python3 is required but not installed."
    exit 1
fi

# Install build tools if not present
log_info "Checking and installing required build tools..."

if ! python3 -c "import build" &> /dev/null; then
    log_info "Installing 'build' package..."
    pip3 install build || {
        log_error "Failed to install 'build' package"
        exit 1
    }
fi

if ! command -v twine &> /dev/null; then
    log_info "Installing 'twine' package..."
    pip3 install twine || {
        log_error "Failed to install 'twine' package"
        exit 1
    }
else
    # Ensure we have the latest version of twine
    log_info "Upgrading twine to latest version..."
    pip3 install --upgrade twine
fi

log_success "All required tools are available"

# Extract current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
log_info "Current version in pyproject.toml: $CURRENT_VERSION"

# Extract version from setup.cfg
SETUP_CFG_VERSION=$(grep '^version = ' setup.cfg | sed 's/version = \(.*\)/\1/')
log_info "Current version in setup.cfg: $SETUP_CFG_VERSION"

# Check if versions are in sync
if [[ "$CURRENT_VERSION" != "$SETUP_CFG_VERSION" ]]; then
    log_error "Version mismatch detected!"
    log_error "  pyproject.toml: $CURRENT_VERSION"
    log_error "  setup.cfg: $SETUP_CFG_VERSION"
    log_error "Please update both files to have the same version number."
    exit 1
fi

log_success "Version numbers are in sync: $CURRENT_VERSION"

# Check if git repository is clean
if ! git diff-index --quiet HEAD --; then
    log_warning "Git repository has uncommitted changes."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Aborting release due to uncommitted changes."
        exit 1
    fi
fi

# Run pre-release checks
log_info "Running pre-release checks..."

# Check that pyproject.toml is valid
log_info "Validating pyproject.toml..."
python3 -c "
try:
    import tomllib
except ImportError:
    import tomli as tomllib
with open('pyproject.toml', 'rb') as f:
    tomllib.load(f)
" 2>/dev/null || {
    log_warning "Could not validate pyproject.toml (install tomli for older Python versions)"
}

# Run linting and type checking
log_info "Running code quality checks..."
if command -v ruff &> /dev/null; then
    ruff check gst.py || {
        log_error "Ruff linting failed"
        exit 1
    }
    log_success "Ruff linting passed"
else
    log_warning "Ruff not found, skipping linting"
fi

if command -v mypy &> /dev/null; then
    mypy gst.py || {
        log_error "MyPy type checking failed"
        exit 1
    }
    log_success "MyPy type checking passed"
else
    log_warning "MyPy not found, skipping type checking"
fi

# Clean previous builds
log_info "Cleaning previous build artifacts..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# Build the package
log_info "Building package..."
python3 -m build

# Check that build was successful
if [[ ! -f "dist/gst-${CURRENT_VERSION}-py3-none-any.whl" ]]; then
    log_error "Wheel build failed - expected file not found"
    exit 1
fi

if [[ ! -f "dist/gst-${CURRENT_VERSION}.tar.gz" ]]; then
    log_error "Source distribution build failed - expected file not found"
    exit 1
fi

log_success "Package built successfully"

# Check the built package
log_info "Checking built package with twine..."
twine check dist/* || {
    log_error "Package check failed"
    exit 1
}
log_success "Package check passed"

# Show what will be uploaded
log_info "Built packages:"
ls -la dist/

# Confirm upload
echo ""
if [[ "$USE_TEST_PYPI" == true ]]; then
    log_warning "About to upload version $CURRENT_VERSION to TestPyPI"
    echo "TestPyPI URL: https://test.pypi.org/project/gst/"
else
    log_warning "About to upload version $CURRENT_VERSION to PyPI"
    echo "PyPI URL: https://pypi.org/project/gst/"
fi

read -p "Continue with upload? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_error "Upload cancelled by user"
    exit 1
fi

# Upload to PyPI or TestPyPI
log_info "Uploading to $(if [[ "$USE_TEST_PYPI" == true ]]; then echo "TestPyPI"; else echo "PyPI"; fi)..."

if [[ "$USE_TEST_PYPI" == true ]]; then
    # Upload to TestPyPI
    twine upload --repository testpypi dist/* || {
        log_error "Upload to TestPyPI failed"
        exit 1
    }
    log_success "Successfully uploaded to TestPyPI!"
    echo "View at: https://test.pypi.org/project/gst/"
    echo "Install with: pip install -i https://test.pypi.org/simple/ gst"
else
    # Upload to PyPI
    twine upload dist/* || {
        log_error "Upload to PyPI failed"
        exit 1
    }
    log_success "Successfully uploaded to PyPI!"
    echo "View at: https://pypi.org/project/gst/"
    echo "Install with: pip install gst"
fi

# Create git tag
log_info "Creating git tag v$CURRENT_VERSION..."
if git tag -a "v$CURRENT_VERSION" -m "Release version $CURRENT_VERSION"; then
    log_success "Git tag created: v$CURRENT_VERSION"
    echo "Push the tag with: git push origin v$CURRENT_VERSION"
else
    log_warning "Git tag creation failed (tag may already exist)"
fi

# Final instructions
echo ""
log_success "Release process completed!"
echo ""
echo "Next steps:"
echo "1. Push the git tag: git push origin v$CURRENT_VERSION"
echo "2. Create a GitHub release with the changelog"
echo "3. Test the installation: pip install gst==$CURRENT_VERSION"
echo ""
