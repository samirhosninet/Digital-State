"""Unit Tests for Phase 1 Bootstrap Subsystem (v1.14.0-bootstrap).

Validates prerequisite checks, dry-run mode, and idempotent workspace installation.
"""

import pytest
from pathlib import Path
from digital_state.bootstrap.prereqs import PrerequisiteChecker
from digital_state.bootstrap.installer import BootstrapInstaller


def test_prerequisite_checker():
    checker = PrerequisiteChecker()
    res = checker.run_all_checks()

    assert "is_healthy" in res
    assert res["python"]["is_supported"] is True
    assert res["tools"]["has_pip"] is True


def test_bootstrap_installer_dry_run(tmp_path):
    installer = BootstrapInstaller(workspace_root=tmp_path)
    res = installer.run_bootstrap(dry_run=True)

    assert res["status"] == "DRY_RUN_SUCCESS"
    assert "planned_directories" in res
    assert not (tmp_path / ".specify").exists()


def test_bootstrap_installer_execution(tmp_path):
    installer = BootstrapInstaller(workspace_root=tmp_path)
    res = installer.run_bootstrap(dry_run=False)

    assert res["status"] == "SUCCESS"
    assert (tmp_path / ".specify").exists()
    assert (tmp_path / ".specify" / "state.json").exists()
    assert (tmp_path / ".specify" / "integration.json").exists()
    assert res["workspace_initialization"]["initialized"] is True
    assert res["device_provisioning"]["provisioned"] is True

    # Verify idempotency by executing a second time
    res2 = installer.run_bootstrap(dry_run=False)
    assert res2["status"] == "SUCCESS"


def test_auto_configure_hermes_manifest_seeding(tmp_path, monkeypatch):
    hermes_dir = tmp_path / "hermes"
    hermes_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HERMES_HOME", str(hermes_dir))

    installer = BootstrapInstaller(workspace_root=tmp_path)
    res = installer.auto_configure_hermes()

    assert res["detected"] is True
    assert res["profiles_seeded"] == ["prime", "builder", "auditor"]
    assert (hermes_dir / "profiles" / "prime" / "profile.yaml").exists()
    assert (hermes_dir / "profiles" / "builder" / "profile.yaml").exists()
    assert (hermes_dir / "profiles" / "auditor" / "profile.yaml").exists()


