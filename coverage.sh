#!/usr/bin/env bash

uv run pytest --cov=pywrapper --cov-report=term-missing --cov-report=html tests/
