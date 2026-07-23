"""Automated test suite for single-command installation experience (User Installation Experience Layer).

Simulates a clean environment checkout and verifies that executing a single install
command (`digitalstate install` or UserInstaller) initializes Digital State to a READY
state and generates the verifiable `.specify/installation_report.json` evidence report.
"""

import json
import os
import tempfile
import pytest
from digital_state.cli.cli import run_cli
from digital_state.cli.installer import UserInstaller


def test_single_command_installation_flow_clean_environment():
    """Verify single-command installation experience on a fresh clean workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        assert not os.path.exists(specify_dir)

        # 1. Execute single install command via CLI
        code = run_cli(["install"], workspace_root=tmpdir)
        assert code == 0

        # 2. Verify workspace structure, configs, and memory directories created
        assert os.path.exists(specify_dir)
        assert os.path.exists(os.path.join(specify_dir, "integration.json"))
        assert os.path.exists(os.path.join(specify_dir, "init-options.json"))
        assert os.path.exists(os.path.join(specify_dir, "state.json"))
        assert os.path.exists(os.path.join(specify_dir, "memory", "audit_log.jsonl"))

        # 3. Verify installation_report.json evidence report exists and contains READY status
        report_path = os.path.join(specify_dir, "installation_report.json")
        assert os.path.exists(report_path)

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        assert report["runtime"] == "READY"
        assert report["governance"] == "READY"
        assert report["hermes"] == "CONNECTED"
        assert report["doctor"] == "PASS"


def test_user_installer_dry_run_and_text_rendering(capsys):
    """Verify dry-run mode and user-facing text report output rendering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        installer = UserInstaller(workspace_root=tmpdir)
        report = installer.run_installation(dry_run=True)
        assert report["doctor"] == "PASS"

        installer.render_report_text(report)
        out, _ = capsys.readouterr()
        assert "Digital State Single-Command Installation Experience" in out
        assert "INSTALLATION STATUS: Digital State READY" in out
