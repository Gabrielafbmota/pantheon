#!/usr/bin/env bash
# Aegis Global Installer
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛡️  Aegis Global Installer"
echo "========================="
echo ""

# Check for pipx
if ! command -v pipx >/dev/null 2>&1; then
    echo "❌ ERROR: pipx is not installed."
    echo ""
    echo "Please install pipx first:"
    echo "  python -m pip install --user pipx"
    echo "  python -m pipx ensurepath"
    echo ""
    echo "Then restart your shell and run this script again."
    exit 1
fi

# Check for poetry
if ! command -v poetry >/dev/null 2>&1; then
    echo "❌ ERROR: poetry is not installed."
    echo ""
    echo "Please install poetry first:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    echo ""
    echo "Or visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
poetry install --no-interaction

# Build package
echo "🔨 Building package..."
poetry build

# Get the wheel file name
WHEEL_FILE=$(ls -1t dist/*.whl | head -n1)

if [ -z "$WHEEL_FILE" ]; then
    echo "❌ ERROR: No wheel file found in dist/"
    exit 1
fi

echo "📦 Found: $WHEEL_FILE"

# Install with pipx
echo "🚀 Installing globally with pipx..."
pipx install --force "$WHEEL_FILE"

echo ""
echo "✅ Aegis installed successfully!"
echo ""
echo "You can now use Aegis from anywhere:"
echo "  aegis scan --repo . --output -"
echo "  aegis persist --input-file report.json"
echo ""
echo "To uninstall:"
echo "  pipx uninstall aegis"
echo ""
