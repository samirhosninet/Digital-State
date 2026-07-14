#!/bin/bash
# Digital State Linux/macOS Installer Script (install.sh)
# Verifies environment, installs dependencies, and runs workspace bootstrap.

set -e

echo -e "\033[0;36m============================================="
echo -e "  Digital State Governance Installer (Unix)"
echo -e "=============================================\033[0m"

# 1. Validate Python >= 3.11 prerequisite
echo -e "\033[0;33m[1/3] Checking Python prerequisite...\033[0m"
if ! command -v python3 &> /dev/null; then
    echo -e "\033[0;31mError: python3 is not installed or not available in PATH.\033[0m" >&2
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

echo -e "Found Python version: $PY_VERSION"

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
    echo -e "\033[0;31mError: Python 3.11 or higher is required. Found version: $PY_VERSION\033[0m" >&2
    exit 1
fi

# 2. Install Project Dependencies
echo -e "\033[0;33m[2/3] Installing Digital State package dependencies...\033[0m"
if command -v uv &> /dev/null; then
    echo "Found 'uv' package manager. Installing with uv..."
    uv pip install -e .
else
    echo "'uv' not found. Installing with pip..."
    pip install -e .
fi

# 3. Initialize workspace
echo -e "\033[0;33m[3/3] Bootstrapping workspace state...\033[0m"

LOCAL_BIN="./.venv/bin/digitalstate"
LOCAL_PYTHON="./.venv/bin/python"

if [ -f "$LOCAL_BIN" ]; then
    echo "Running bootstrap via local virtualenv CLI..."
    "$LOCAL_BIN" init
elif [ -f "$LOCAL_PYTHON" ]; then
    echo "Running bootstrap via local virtualenv Python..."
    export PYTHONPATH="src"
    "$LOCAL_PYTHON" -m digital_state.cli.cli init
elif command -v digitalstate &> /dev/null; then
    digitalstate init
else
    echo "Running bootstrap via system Python..."
    python3 -m digital_state.cli.cli init
fi

echo ""
echo -e "\033[0;32m============================================="
echo -e "  Digital State Installed Successfully!"
echo -e "=============================================\033[0m"
echo -e "To verify installation, run:"

if [ -f "$LOCAL_BIN" ]; then
    echo -e "  \033[1;37m./.venv/bin/digitalstate doctor\033[0m"
elif [ -f "$LOCAL_PYTHON" ]; then
    echo -e "  \033[1;37m./.venv/bin/python -m digital_state.cli.cli doctor\033[0m"
elif command -v digitalstate &> /dev/null; then
    echo -e "  \033[1;37mdigitalstate doctor\033[0m"
else
    echo -e "  \033[1;37mpython3 -m digital_state.cli.cli doctor\033[0m"
fi
echo ""

