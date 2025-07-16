# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.12] - 2025-07-16 (Python 3.6)

### Fixed
- Use external links in README.md so they work on sites like PyPi

## [0.1.11] - 2025-07-16 (Python 3.6)

### Fixed
- Set applicable Python version to Python 3.6+ in toml file

## [0.1.10] - 2025-07-16 (Python 3.6)

### Added
- Added back support for Python 3.6+ (add back setup.cfg and setup.py).
  - Add logic in update_pypi.sh to ensure versions (in setup.cfg and pyproject.toml) remain in sync.
  - Will support Python 3.6 with best effort with manual tests and periodic releases for Python 3.6 & Python 3.7.
- Added integration tests (for Python 3.8+).
- Add recommendations for improving performance of `gst` on large repos.
- Add CONTRIBUTING.md file.

## [0.1.9] - 2025-07-14

### Fixed
- Switch back to `git status -s` instead of `git status --porcelain` for improved stability

## [0.1.8] - 2025-07-14

### Added
- Add setup_dev.sh script which installs a precommit hook that uses ruff and mypy
- Add update_pypi.sh script
- Add unit tests with pytest

### Changed
- Migrated from setup.py to pyproject.toml
- Reformatted gst.py to follow ruff formatting
- Follow PEP8 naming conventions in gst.py
- Use class in gst.py instead of global variables
- Use `git status --porcelain` instead of `git status -s` for improved stability

### Fixed
- Fixed mypy errors in gst.py
- Fix issue where duplicate folders will not be disambiguated E.g. two folders named `__pycache__/` in different directories

## [0.1.7] - 2025-07-13

### Fixed
- Fixed display of untracked folders which would show up blank without `-v` option.

## [0.1.6] - 2025-07-12

### Added
- Add CHANGELOG to track changes
- Add "edit" command. E.g. `gst -e <REF_INT>` (Thanks to @NeKpoT)
