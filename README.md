# gst [![MIT License][license-badge]](LICENSE.md)

## Synposis
gst is short for **G**it **St**atus - it's a commandline app with some neat features for improving your workflow with git
Note that gst is meant for in dark themed terminals

## Usage

### Basic git status display
```bash
$ gst # Show status of repository
```
![Basic gst output](docs/images/gst-basic.svg)

### Add files to staging area
```bash
$ gst -a 0,1 # Add files by index
```
![After adding files](docs/images/gst-after-add.svg)

### View file differences
```bash
$ gst -d 1 # View changes of a file
```
![Git diff output](docs/images/gst-diff.svg)

### Other useful commands
```bash
$ gst -r 1        # Reset staged changes
$ gst -c 1        # Checkout file to revert changes
$ gst -D 1        # Delete a file
$ gst -e 1        # Open file in default editor
$ gst 1           # Print file path for use in other commands
```

### Range and selection syntax
```bash
$ gst -a 0,2,4    # Add specific files by index
$ gst -a 1:3      # Add files 1, 2, and 3
$ gst -a 2:       # Add files from index 2 to end
$ gst -a 0,2:4,6  # Mix individual and range selections
```

## Installation
Install from pip.
```
pip install gst
```

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

### Running tests
```bash
pytest tests/                    # Run all tests
pytest tests/test_gst.py -v      # Run specific test file with verbose output
```

### Regenerating README images
```bash
python scripts/generate_svg_examples.py
```

## Compatability
- Linux, Mac, Windows
- Git version >2
- Python3 (re: https://pythonclock.org/)

## TODO
- Add more example scenarios
- Consider adding animated GIFs for complex workflows

## License MIT
[View project License](LICENSE.md).

[license-badge]: https://img.shields.io/badge/license-MIT-007EC7.svg
