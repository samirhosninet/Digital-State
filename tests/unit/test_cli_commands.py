import os
import tempfile
import json
import pytest
from digital_state.cli.cli import run_cli

def test_cli_init_command():
    """Verify that 'init' initializes the workspace structure and is idempotent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Before init, specify folder does not exist
        specify_dir = os.path.join(tmpdir, ".specify")
        assert not os.path.exists(specify_dir)

        # Run init command
        code = run_cli(["init"], workspace_root=tmpdir)
        assert code == 0

        # Verify specify folder and config files are created
        assert os.path.exists(specify_dir)
        assert os.path.exists(os.path.join(specify_dir, "integration.json"))
        assert os.path.exists(os.path.join(specify_dir, "init-options.json"))
        assert os.path.exists(os.path.join(specify_dir, "agents.json"))
        assert os.path.exists(os.path.join(specify_dir, "state.json"))
        assert os.path.exists(os.path.join(specify_dir, "memory", "audit_log.jsonl"))

        # Verify agents.json starts empty (for user initialization)
        with open(os.path.join(specify_dir, "agents.json"), "r", encoding="utf-8") as f:
            agents_data = json.load(f)
            assert agents_data == {}

        # Edit agents.json to check idempotency / non-destructive check
        with open(os.path.join(specify_dir, "agents.json"), "w", encoding="utf-8") as f:
            json.dump({"test-agent": {}}, f)

        # Run init again
        code = run_cli(["init"], workspace_root=tmpdir)
        assert code == 0

        # Assert custom agent is preserved (not overwritten)
        with open(os.path.join(specify_dir, "agents.json"), "r", encoding="utf-8") as f:
            agents_data = json.load(f)
            assert "test-agent" in agents_data

def test_cli_doctor_command(capsys):
    """Verify that 'doctor' reports on installation, configuration, and Hermes integration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Before init, config fails
        code = run_cli(["doctor"], workspace_root=tmpdir)
        assert code == 0
        out, _ = capsys.readouterr()
        report = json.loads(out)
        assert report["configuration"]["status"] == "FAIL"

        # Initialize
        run_cli(["init"], workspace_root=tmpdir)
        capsys.readouterr()

        # Run doctor again
        code = run_cli(["doctor"], workspace_root=tmpdir)
        assert code == 0
        out, _ = capsys.readouterr()
        report = json.loads(out)
        
        assert report["installation"]["status"] == "PASS"
        assert report["configuration"]["status"] == "PASS"
        assert report["governance"]["status"] == "PASS"
        assert report["hermes"]["is_mock_adapter"] is False
        assert report["hermes"]["status"] == "PASS"

def test_cli_repair_command():
    """Verify that 'repair' validates and recreates workspace database files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run repair on an uninitialized directory
        code = run_cli(["repair"], workspace_root=tmpdir)
        assert code == 0
        specify_dir = os.path.join(tmpdir, ".specify")
        assert os.path.exists(os.path.join(specify_dir, "state.json"))
        assert os.path.exists(os.path.join(specify_dir, "agents.json"))

def test_cli_upgrade_command(monkeypatch):
    """Verify that 'upgrade' parses successfully and handles missing environment check."""
    # When no Hermes virtualenv is available, upgrade must return 1
    with tempfile.TemporaryDirectory() as tmpdir:
        code = run_cli(["upgrade"], workspace_root=tmpdir)
        assert code == 1

def test_cli_uninstall_command():
    """Verify that 'uninstall' runs cleanly and reports success status."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Uninstall should clean up profile directories and return 0
        code = run_cli(["uninstall"], workspace_root=tmpdir)
        assert code == 0
