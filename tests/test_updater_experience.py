"""Automated test suite for official update lifecycle experience (digitalstate update).

Verifies version detection, update checks, non-destructive migration execution,
rollback protection on migration failures, preservation of RuntimeStore identities and
governance evidence, and update evidence report generation (.specify/update_report.json).
"""

import json
import os
import tempfile
import pytest
from digital_state.cli.cli import run_cli
from digital_state.cli.updater import UserUpdater


def test_update_no_update_available():
    """Verify that running update when already up-to-date returns NO_UPDATE_REQUIRED."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # First install to populate workspace
        run_cli(["install"], workspace_root=tmpdir)

        # Run update check
        updater = UserUpdater(workspace_root=tmpdir)
        report = updater.run_update(check_only=False, force=False)

        assert report["migration_status"] == "NO_UPDATE_REQUIRED"
        assert report["doctor_status"] == "PASS"
        assert report["runtime_status"] == "READY"
        assert report["governance_status"] == "READY"

        # Verify update_report.json was generated
        report_path = os.path.join(tmpdir, ".specify", "update_report.json")
        assert os.path.exists(report_path)


def test_update_successful_migration_and_evidence_preservation():
    """Verify successful version migration preserving user workspace, RuntimeStore, and evidence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Initialize & install workspace
        assert run_cli(["install"], workspace_root=tmpdir) == 0
        specify_dir = os.path.join(tmpdir, ".specify")

        # 2. Add custom governance evidence log entry
        log_path = os.path.join(specify_dir, "memory", "audit_log.jsonl")
        custom_entry = json.dumps({"event": "PRE_UPDATE_EVIDENCE", "id": 9999}) + "\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(custom_entry)

        # 3. Add custom state entry
        state_path = os.path.join(specify_dir, "state.json")
        with open(state_path, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        state_data["pre_update_feature"] = "PRESERVED"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f)

        # 4. Run update with new target version
        updater = UserUpdater(workspace_root=tmpdir)
        report = updater.run_update(target_version="1.17.0", force=True)

        assert report["migration_status"] == "SUCCESS"
        assert report["target_version"] == "1.17.0"
        assert report["doctor_status"] == "PASS"

        # 5. Assert governance evidence log is preserved
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "PRE_UPDATE_EVIDENCE" in content

        # 6. Assert state.json features are preserved
        with open(state_path, "r", encoding="utf-8") as f:
            updated_state = json.load(f)
            assert updated_state.get("pre_update_feature") == "PRESERVED"


def test_update_failed_migration_rollback_contract():
    """Verify that a migration failure executes safe rollback without corrupting workspace or evidence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize & install workspace
        assert run_cli(["install"], workspace_root=tmpdir) == 0
        specify_dir = os.path.join(tmpdir, ".specify")

        # Write sentinel data before update attempt
        sentinel_file = os.path.join(specify_dir, "sentinel.txt")
        with open(sentinel_file, "w", encoding="utf-8") as f:
            f.write("SAFE_GOVERNANCE_DATA")

        # Execute updater with simulated failure
        updater = UserUpdater(workspace_root=tmpdir)
        report = updater.run_update(target_version="2.0.0", force=True, simulate_failure=True)

        assert report["migration_status"] == "FAILED_ROLLED_BACK"
        assert report["doctor_status"] == "FAIL"
        assert report["details"]["rollback_executed"] is True
        assert report["details"]["rollback_success"] is True

        # Assert sentinel file was restored during rollback
        assert os.path.exists(sentinel_file)
        with open(sentinel_file, "r", encoding="utf-8") as f:
            assert f.read() == "SAFE_GOVERNANCE_DATA"


def test_cli_version_and_update_commands(capsys):
    """Verify 'digitalstate version' and 'digitalstate update' CLI invocation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test version command
        assert run_cli(["version"], workspace_root=tmpdir) == 0
        out, _ = capsys.readouterr()
        assert "digitalstate version 1.16.0" in out

        # Test version json format
        assert run_cli(["version", "--format", "json"], workspace_root=tmpdir) == 0
        out, _ = capsys.readouterr()
        ver_data = json.loads(out)
        assert ver_data["version"] == "1.16.0"

        # Install workspace
        run_cli(["install"], workspace_root=tmpdir)
        capsys.readouterr()

        # Test update command
        assert run_cli(["update", "--check"], workspace_root=tmpdir) == 0
        out, _ = capsys.readouterr()
        assert "Digital State Official Update Lifecycle Experience" in out
