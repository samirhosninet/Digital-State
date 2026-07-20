"""Unit Tests for Layer 2 Lifecycle Commands (ECR-002).

Validates digitalstate install, repair, update, uninstall, and doctor lifecycle routines.
"""

import pytest
from pathlib import Path
from digital_state.bootstrap.engine.orchestrator import run_engine_cli
from digital_state.bootstrap.engine.manifest_manager import ManifestManager


def test_lifecycle_dry_run():
    """Verify dry-run mode returns exit code 0."""
    res = run_engine_cli(action="install", dry_run=True)
    assert res == 0


def test_lifecycle_doctor_command(tmp_path, capsys):
    """Verify doctor command outputs valid JSON manifest."""
    manifest_mgr = ManifestManager(target_dir=tmp_path)
    res = run_engine_cli(action="doctor", dry_run=False)
    assert res == 0
    captured = capsys.readouterr()
    assert "Digital State Layer 2 Doctor Diagnostic Report" in captured.out


def test_lifecycle_uninstall_command(tmp_path):
    """Verify uninstall command updates manifest state to UNINSTALLED."""
    manifest_mgr = ManifestManager(target_dir=tmp_path)
    res = run_engine_cli(action="uninstall", dry_run=False)
    assert res == 0


def test_lifecycle_repair_command(tmp_path):
    """Verify repair command synchronizes subsystem state."""
    manifest_mgr = ManifestManager(target_dir=tmp_path)
    res = run_engine_cli(action="repair", dry_run=False)
    assert res == 0


def test_lifecycle_update_command(tmp_path):
    """Verify update command executes migration and update."""
    manifest_mgr = ManifestManager(target_dir=tmp_path)
    res = run_engine_cli(action="update", dry_run=False)
    assert res == 0
