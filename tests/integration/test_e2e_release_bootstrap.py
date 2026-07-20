"""End-to-End Release Bootstrap Integration Test (ECR-002).

Validates complete installation lifecycle from Layer 1 Stub through Layer 2 Engine to Layer 3 Runtime.
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from digital_state.bootstrap.engine.manifest_manager import ManifestManager


def test_e2e_layer1_to_layer3_bootstrap_flow(tmp_path):
    """Verifies complete end-to-end zero-touch bootstrap execution."""
    if sys.platform != "win32":
        pytest.skip("PowerShell E2E test skipped on non-Windows platform")

    repo_root = Path(__file__).resolve().parents[2]
    ps_script = repo_root / "install.ps1"
    assert ps_script.exists()

    # 1. Execute Layer 1 Stub in DryRun mode
    env = os.environ.copy()
    env["DS_DRY_RUN"] = "1"
    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        f"Get-Content '{ps_script}' -Raw | Invoke-Expression"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root), env=env)
    assert res.returncode == 0
    assert "Layer 2 Installer Engine (DRY RUN MODE)" in res.stdout

    # 2. Execute Layer 2 Engine Orchestrator install in workspace
    from digital_state.bootstrap.engine.orchestrator import run_engine_cli
    install_rc = run_engine_cli("install", dry_run=False, workspace_root=tmp_path)
    assert install_rc == 0

    # 3. Verify Layer 3 Canonical Manifest is created and fully integrated
    manifest_mgr = ManifestManager()
    manifest = manifest_mgr.load_manifest()
    assert manifest["installation_state"] == "FULLY_INTEGRATED"
    assert manifest["health_status"] == "PASS"
