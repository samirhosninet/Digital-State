"""Unit Tests for Layer 2 ManifestManager and LockManager (ECR-002)."""

import pytest
from pathlib import Path
from digital_state.bootstrap.engine.manifest_manager import ManifestManager
from digital_state.bootstrap.engine.lock_manager import LockManager


def test_manifest_manager_crud(tmp_path):
    """Verify ManifestManager saves and loads installation.json canonical manifest correctly."""
    mgr = ManifestManager(target_dir=tmp_path)
    manifest = mgr.load_manifest()

    assert manifest["installation_state"] == "NOT_INSTALLED"
    assert manifest["installer_version"] == "1.16.0"

    # Modify and save
    manifest["installation_state"] = "FULLY_INTEGRATED"
    manifest["health_status"] = "PASS"
    assert mgr.save_manifest(manifest) is True

    # Reload and verify
    reloaded = mgr.load_manifest()
    assert reloaded["installation_state"] == "FULLY_INTEGRATED"
    assert reloaded["health_status"] == "PASS"


def test_lock_manager_concurrency(tmp_path):
    """Verify LockManager acquires and releases cross-process lock file."""
    lock_mgr = LockManager(lock_dir=tmp_path)
    assert lock_mgr.acquire() is True

    # Second lock acquisition attempt should fail timeout
    lock_mgr2 = LockManager(lock_dir=tmp_path)
    assert lock_mgr2.acquire(timeout_sec=0.2) is False

    lock_mgr.release()
    assert lock_mgr2.acquire(timeout_sec=0.2) is True
    lock_mgr2.release()
