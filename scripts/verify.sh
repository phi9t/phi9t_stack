#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$ROOT"
uv run --locked ruff format --check scripts tests skills
uv run --locked ruff check scripts tests skills
uv run --locked ty check scripts/stack.py scripts/release.py skills/phi9t-land/scripts/land.py
uv run --locked shellcheck scripts/*.sh
uv run --locked python scripts/vendor.py check
uv run --locked python scripts/stack.py check
exec uv run --locked python -m unittest discover -s tests -v
