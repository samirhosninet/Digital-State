"""Unit Tests for Phase 3 CLI Subcommand Evidence Verification (v1.13.0-platform).

Validates CLI audit-evidence --check, --all, --format json/markdown options and exit codes.
"""

import json
import pytest
from digital_state.cli.cli import run_cli


def test_cli_audit_evidence_empty():
    ret = run_cli(["audit-evidence"])
    assert ret == 0


def test_cli_audit_evidence_file(tmp_path):
    manifest_file = tmp_path / "evidence_manifest.json"
    manifest_data = {
        "records": [
            {
                "statement": "Valid pyproject.toml registration",
                "evidence_type": "Repository Implementation Evidence",
                "boundary": "Digital State Repository",
                "source": "pyproject.toml entrypoint",
                "classification": "VERIFIED",
                "justification": "Entrypoint is registered in pyproject.toml",
                "repo_path": "pyproject.toml"
            }
        ]
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # Markdown format
    ret_md = run_cli(["audit-evidence", "--file", str(manifest_file), "--format", "markdown"])
    assert ret_md == 0

    # JSON format
    ret_json = run_cli(["audit-evidence", "--file", str(manifest_file), "--format", "json"])
    assert ret_json == 0

    # Check mode pass
    ret_check_pass = run_cli(["audit-evidence", "--file", str(manifest_file), "--check"])
    assert ret_check_pass == 0


def test_cli_audit_evidence_check_fail(tmp_path):
    manifest_file = tmp_path / "failing_manifest.json"
    manifest_data = {
        "records": [
            {
                "statement": "Unverified external claim",
                "evidence_type": "External Runtime Behavior",
                "boundary": "External Platform Behavior",
                "source": "unverified",
                "classification": "VERIFIED",
                "justification": "Unverified claim"
            }
        ]
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # Engine degrades to UNVERIFIED, check mode should return non-zero exit code 1
    ret_check_fail = run_cli(["audit-evidence", "--file", str(manifest_file), "--check"])
    assert ret_check_fail == 1


def test_cli_audit_evidence_all():
    ret_all = run_cli(["audit-evidence", "--all", "--format", "json"])
    assert ret_all == 0
