#!/usr/bin/env bash
set -euo pipefail

# Helper to run aegis via poetry from inside services/aegis
cd "$(dirname "$0")"

if ! command -v poetry >/dev/null 2>&1; then
  echo "poetry is required. Install it: https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <aegis-args>" >&2
  echo "Example: $0 scan --repo . --output -" >&2
  exit 1
fi

poetry run aegis "$@"
