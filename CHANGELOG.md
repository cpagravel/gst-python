# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add setup_dev.sh script which installs a precommit hook that uses ruff and mypy
- Add update_pypi.sh script

### Changed
- Migrated from setup.py to pyproject.toml
- Reformatted gst.py to follow ruff formatting
- Follow PEP8 naming conventions in gst.py
- Use class in gst.py instead of global variables

### Fixed
- Fixed mypy errors in gst.py

## [0.1.7] - 2025-07-13

### Fixed
- Fixed display of untracked folders which would show up blank without `-v` option.

## [0.1.6] - 2025-07-12

### Added
- Add CHANGELOG to track changes
- Add "edit" command. E.g. `gst -e <REF_INT>` (Thanks to @NeKpoT)
