"""Unit Tests for Layer 1 Immutable Bootstrap Stub (install.ps1)."""

import os
import sys
import subprocess
import pytest
from pathlib import Path

def test_install_ps1_stub_dry_run(tmp_path):
    """Verify install.ps1 executes in PowerShell dry-run mode and returns exit code 0."""
    if sys.platform != "win32":
        pytest.skip("PowerShell test skipped on non-Windows platform")

    repo_root = Path(__file__).resolve().parents[2]
    ps_script = repo_root / "install.ps1"
    assert ps_script.exists()

    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", str(ps_script),
        "-DryRun"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
    assert res.returncode == 0
    assert "Layer 2 Installer Engine (DRY RUN MODE)" in res.stdout
