#!/usr/bin/env bash
# Digital State Idempotent POSIX Shell Installer (v1.14.0-bootstrap)
# Usage: ./install.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
    if [ "$arg" == "--dry-run" ]; then
        DRY_RUN=true
    fi
done

echo "====================================================="
echo " Digital State Zero-Touch Installer (v1.14.0-bootstrap)"
echo "====================================================="

PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "Error: Python 3.11+ is required but not found in PATH." >&2
    exit 1
fi

PY_VERSION=$("$PYTHON_BIN" --version 2>&1)
echo "[+] Detected: $PY_VERSION"

export PYTHONPATH="src:${PYTHONPATH:-}"

if [ "$DRY_RUN" = true ]; then
    echo "[*] Executing Dry-Run Verification..."
    "$PYTHON_BIN" -c "import sys; sys.path.insert(0, 'src'); from digital_state.bootstrap.installer import BootstrapInstaller; res = BootstrapInstaller().run_bootstrap(dry_run=True); print(res); sys.exit(0 if res.get('status') == 'DRY_RUN_SUCCESS' else 1)"
else
    echo "[*] Executing Idempotent Workspace Installation..."
    "$PYTHON_BIN" -c "import sys; sys.path.insert(0, 'src'); from digital_state.bootstrap.installer import BootstrapInstaller; res = BootstrapInstaller().run_bootstrap(dry_run=False); print(res); sys.exit(0 if res.get('status') == 'SUCCESS' else 1)"
fi

echo "[✓] Digital State Installation Completed Successfully."
