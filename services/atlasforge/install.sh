#!/bin/bash
# AtlasForge Global Installation Script
# This script installs AtlasForge globally using pipx

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AtlasForge Global Installer          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}⚠️  pipx is not installed${NC}"
    echo -e "${BLUE}Installing pipx...${NC}"

    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update && sudo apt-get install -y pipx
        pipx ensurepath
    elif command -v brew &> /dev/null; then
        # macOS
        brew install pipx
        pipx ensurepath
    else
        # Try pip
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
    fi

    echo -e "${GREEN}✅ pipx installed${NC}"
    echo -e "${YELLOW}⚠️  You may need to restart your shell or run: source ~/.bashrc${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Error: Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo ""

# Install AtlasForge
echo -e "${BLUE}📦 Installing AtlasForge globally...${NC}"
pipx install --force .

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Installation Complete!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Verify installation
if command -v atlasforge &> /dev/null; then
    echo -e "${BLUE}Version installed:${NC}"
    atlasforge version
    echo ""
    echo -e "${BLUE}📚 Quick start:${NC}"
    echo -e "  ${GREEN}atlasforge generate my-service${NC}        # Generate new project"
    echo -e "  ${GREEN}atlasforge --help${NC}                      # Show all commands"
    echo ""
    echo -e "${BLUE}📖 Documentation:${NC} services/atlasforge/IMPLEMENTATION.md"
else
    echo -e "${YELLOW}⚠️  AtlasForge installed but not in PATH${NC}"
    echo -e "${YELLOW}   Run: pipx ensurepath${NC}"
    echo -e "${YELLOW}   Then restart your shell${NC}"
fi

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
