"""Unit Tests for Phase 1 Bootstrap Subsystem (v1.14.0-bootstrap).

Validates prerequisite checks, dry-run mode, idempotent workspace installation,
and the package-root resolver that guards against bogus `pip install` targets.
"""

import os
import pytest
from pathlib import Path
from digital_state.bootstrap.prereqs import PrerequisiteChecker
from digital_state.bootstrap.installer import BootstrapInstaller


def test_resolve_package_root_uses_ds_package_root(tmp_path, monkeypatch):
    """_resolve_package_root must honor DS_PACKAGE_ROOT when it contains pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    monkeypatch.setenv("DS_PACKAGE_ROOT", str(tmp_path))
    inst = BootstrapInstaller(workspace_root=Path("/nonexistent-cwd"))
    assert inst._resolve_package_root() == tmp_path.resolve()


def test_resolve_package_root_rejects_bogus_env(monkeypatch, tmp_path):
    """When DS_PACKAGE_ROOT points at a non-source dir, it must NOT be returned."""
    monkeypatch.setenv("DS_PACKAGE_ROOT", str(tmp_path))  # no pyproject.toml here
    inst = BootstrapInstaller(workspace_root=tmp_path)
    resolved = inst._resolve_package_root()
    # The bogus env dir must never be returned...
    assert resolved != tmp_path
    # ...and the result must point at a real source tree containing pyproject.toml
    # (here the repo root D:/Digital-State, discovered by the upward search).
    assert (resolved / "pyproject.toml").exists()


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


def test_auto_provision_device_evidence_enrollment(tmp_path):
    device_dir = tmp_path / ".specify" / "device"
    installer = BootstrapInstaller(workspace_root=tmp_path)
    res = installer.auto_provision_device_evidence(device_dir=device_dir)

    assert res["provisioned"] is True
    assert res["enrolled"] is True
    assert "certificate_id" in res
    assert (device_dir / "device-certificate.json").exists()


def test_verify_installation_health(tmp_path):
    device_dir = tmp_path / ".specify" / "device"
    installer = BootstrapInstaller(workspace_root=tmp_path)
    installer.auto_provision_device_evidence(device_dir=device_dir)

    res = installer.verify_installation_health(device_dir=device_dir)
    assert res["health_verified"] is True
    assert res["doctor_status"] == "PASS"
    assert res["evidence_records_count"] >= 3




