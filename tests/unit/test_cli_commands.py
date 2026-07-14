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
        assert report["hermes"]["is_mock_adapter"] is True
        assert report["hermes"]["status"] == "WARNING"  # Warns about mock adapter
