"""Unit Tests for Layer 2 Engine Subsystems (ECR-002).

Validates DependencyManager, HermesProvisioner, PluginRegistrar, VerificationEngine, and RollbackEngine.
"""

import pytest
from pathlib import Path
from digital_state.bootstrap.engine.dep_manager import DependencyManager
from digital_state.bootstrap.engine.hermes_provisioner import HermesProvisioner
from digital_state.bootstrap.engine.plugin_registrar import PluginRegistrar
from digital_state.bootstrap.engine.verifier import VerificationEngine
from digital_state.bootstrap.engine.rollback import RollbackEngine
from digital_state.bootstrap.engine.migration import MigrationEngine


def test_dependency_manager_verification():
    """Verify DependencyManager detects Python environment."""
    dep_mgr = DependencyManager()
    res = dep_mgr.verify_dependencies()

    assert res["python_installed"] is True
    assert res["supported"] is True


def test_hermes_provisioner_runtime_resolution(tmp_path):
    """Verify HermesProvisioner resolves Hermes directory."""
    provisioner = HermesProvisioner(override_root=tmp_path)
    res = provisioner.provision_hermes_runtime()

    assert res["detected"] is True
    assert res["hermes_root"] == str(tmp_path)


def test_plugin_registrar_atomic_config_and_profiles(tmp_path):
    """Verify PluginRegistrar enables plugin in config.yaml and seeds profile manifests."""
    registrar = PluginRegistrar(hermes_root=tmp_path)

    # Register plugin
    assert registrar.register_plugin() is True
    assert (tmp_path / "config.yaml").exists()

    # Seed profiles
    p_res = registrar.seed_profiles()
    assert p_res["all_seeded"] is True
    assert (tmp_path / "profiles" / "prime" / "profile.yaml").exists()
    assert (tmp_path / "profiles" / "builder" / "profile.yaml").exists()
    assert (tmp_path / "profiles" / "auditor" / "profile.yaml").exists()


def test_rollback_engine_backup_restoration(tmp_path):
    """Verify RollbackEngine restores backups and purges created files."""
    rollback_mgr = RollbackEngine()

    orig_file = tmp_path / "config.yaml"
    bak_file = tmp_path / "config.yaml.bak"

    orig_file.write_text("modified_content", encoding="utf-8")
    bak_file.write_text("original_content", encoding="utf-8")

    rollback_mgr.register_backup(orig_file, bak_file)
    rollback_mgr.rollback()

    assert orig_file.read_text(encoding="utf-8") == "original_content"


def test_migration_engine():
    """Verify MigrationEngine upgrades manifest runtime version."""
    migration = MigrationEngine(current_version="1.16.0")
    old_manifest = {"runtime_version": "1.15.0"}
    new_manifest = migration.migrate(old_manifest)

    assert new_manifest["runtime_version"] == "1.16.0"
    assert "Upgraded from 1.15.0 to 1.16.0" in new_manifest["migration_note"]
