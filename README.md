# gst [![MIT License][license-badge]](LICENSE.md) [![Tests][tests-badge]][tests-url] [![Coverage][coverage-badge]][coverage-url]

## Synposis
gst is short for **G**it **St**atus - it's a commandline app with some neat features for improving your workflow with git
Note that gst is meant for in dark themed terminals

## Installation
Install from pip.
```
pip install gst
```

## Usage

```bash
$ gst              # View git status
```
![Initial git status](docs/images/demo-01-status.svg)

```bash
$ gst 1            # Get file path by reference
```
![File reference output](docs/images/demo-02-reference.svg)

```bash
$ gst -a 0         # Add files to staging area
```
![After adding file](docs/images/demo-03-after-add.svg)

```bash
$ gst -r 0         # Reset staged changes
```
![After reset](docs/images/demo-04-after-reset.svg)

```bash
$ gst -c 1         # Checkout files to revert changes
```
![After checkout](docs/images/demo-05-after-checkout.svg)

```bash
$ gst -D 2         # Delete files at index
```
![After delete](docs/images/demo-06-after-delete.svg)

```bash
$ gst -d 1         # View file differences
```
![Git diff output](docs/images/demo-07-diff.svg)

```bash
$ gst -e 1         # Open file in editor
```

```bash
# Use file references with other commands
$ cat $(gst 1)     # Display contents of file at index 1
$ vim $(gst 1)     # Open file at index 1 in vim
```

### Range and selection syntax
All commands that accept `REF_RANGE` support flexible selection patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| `0,2,4` | Specific indices | `gst -a 0,2,4` |
| `1:3` | Range (inclusive) | `gst -r 1:3` |
| `2:` | Unbounded range | `gst -c 2:` |
| `0,2:4,6` | Mixed patterns | `gst -D 0,2:4,6` |

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing guidelines, and how to contribute to the project.

## Compatibility
- Linux, Mac, Windows
- Git version >=2
- Python 3.8+ (fully tested and supported)
- Python 3.6, 3.7 (best-effort support with manual testing)

### Python Version Support Policy
- **Python 3.8+**: Fully supported with automated testing in CI/CD
- **Python 3.6, 3.7**: Best-effort support with periodic manual testing for compatibility

Due to [GitHub Actions dropping support for Python 3.6 and 3.7](https://github.com/actions/runner-images/issues/10893), we can no longer provide automated testing for these versions. However, we will continue to maintain compatibility when possible and provide periodic updates with manual testing to confirm functionality.

## Performance Optimization

Since `gst` relies on `git status`, optimizing git performance will directly improve `gst` performance. These settings can provide 50-75% faster operations for large repositories:

```bash
# Enable all git performance optimizations
git config core.fsmonitor true          # File system monitor (Windows/macOS only)
git config core.untrackedCache true     # Cache untracked file detection
git config feature.manyFiles true       # Optimize for large repositories
```

**Features:**
- **FSMonitor**: Background file monitoring, up to 75% faster (not supported on Linux)
- **Untracked Cache**: Faster detection of untracked files
- **feature.manyFiles**: Optimized index format for repositories with many files

**Note:** FSMonitor provides the biggest performance boost for large repositories but may add overhead for small repositories.

## License MIT
[View project License](LICENSE.md).

[license-badge]: https://img.shields.io/badge/license-MIT-007EC7.svg
[tests-badge]: https://github.com/cpagravel/gst-python/workflows/Tests/badge.svg
[tests-url]: https://github.com/cpagravel/gst-python/actions/workflows/test.yml
[coverage-badge]: https://codecov.io/gh/cpagravel/gst-python/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/cpagravel/gst-python
