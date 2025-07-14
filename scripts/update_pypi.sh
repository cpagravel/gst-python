#!/bin/bash

# Use this script to push an update to PyPI.
rm -rf dist/
rm -rf build/
python3 setup.py sdist build
twine upload dist/*
