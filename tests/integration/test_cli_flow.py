import os
import tempfile
import json
import pytest
from unittest.mock import patch

from digital_state.cli.cli import run_cli
from digital_state.core.engine import GovernanceKernel

from tests.conftest import public_key_dict, sign_payload


def _write_public_key_file(tmpdir: str, role: str) -> str:
    """Write a role's ECDSA P-256 public key (PEM) to a temp file and return its path."""
    identity = public_key_dict(role)
    path = os.path.join(tmpdir, f"{role}_public.pem")
    with open(path, "w", encoding="utf-8") as f:
        f.write(identity["value"])
    return path


def test_cli_end_to_end_flow(capsys):
    """Verify that the CLI command endpoints successfully coordinate the entire governance cycle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Setup workspace options
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        feature_id = "feat-cli-flow"

        # Check initial status
        code = run_cli(["status", "--feature", feature_id], workspace_root=tmpdir)
        assert code == 0
        out, _ = capsys.readouterr()
        status_data = json.loads(out)
        assert status_data["current_state"] == "SPECIFICATION"
        assert len(status_data["history"]) == 0

        # Register custom builder agent via CLI using spec 009's contract:
        # --public-key-file + --key-id (ECDSA P-256 public key identity).
        builder_pub_path = _write_public_key_file(tmpdir, "builder")
        code = run_cli([
            "register",
            "--id", "custom-builder",
            "--role", "Builder",
            "--public-key-file", builder_pub_path,
            "--key-id", "key-builder",
        ], workspace_root=tmpdir)
        assert code == 0
        out, _ = capsys.readouterr()
        assert "registered successfully" in out

        # Submit SPECIFICATION evidence (spec 009: submission alone does not
        # advance state; an independent auditor must approve the gate).
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        spec_sig = sign_payload("prime", spec_content)
        spec_content["signature"] = spec_sig

        code = run_cli([
            "submit",
            "--feature", feature_id,
            "--gate", "SPECIFICATION",
            "--evidence", json.dumps(spec_content),
            "--agent", "prime-agent"
        ], workspace_root=tmpdir)
        assert code == 0
        capsys.readouterr()

        # Independent auditor approval transitions SPECIFICATION -> PLANNING
        code = run_cli([
            "approve",
            "--feature", feature_id,
            "--gate", "SPECIFICATION",
            "--agent", "auditor-agent"
        ], workspace_root=tmpdir)
        assert code == 0
        capsys.readouterr()

        # Check state transitioned to PLANNING
        run_cli(["status", "--feature", feature_id], workspace_root=tmpdir)
        out, _ = capsys.readouterr()
        status_data = json.loads(out)
        assert status_data["current_state"] == "PLANNING"
        assert len(status_data["history"]) == 1
        assert status_data["history"][0]["to_state"] == "PLANNING"

        # 4. Submit PLANNING evidence via custom-builder agent (real ECDSA signature)
        plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        plan_sig = sign_payload("builder", plan_content)
        plan_content["signature"] = plan_sig

        code = run_cli([
            "submit",
            "--feature", feature_id,
            "--gate", "PLANNING",
            "--evidence", json.dumps(plan_content),
            "--agent", "custom-builder"
        ], workspace_root=tmpdir)
        assert code == 0
        capsys.readouterr()

        # 5. Approve PLANNING transition to TASKS via auditor-agent
        code = run_cli([
            "approve",
            "--feature", feature_id,
            "--gate", "PLANNING",
            "--agent", "auditor-agent"
        ], workspace_root=tmpdir)
        assert code == 0
        capsys.readouterr()

        # 6. Verify status transitioned to TASKS
        run_cli(["status", "--feature", feature_id], workspace_root=tmpdir)
        out, _ = capsys.readouterr()
        status_data = json.loads(out)
        assert status_data["current_state"] == "TASKS"
        assert len(status_data["history"]) == 2
        assert status_data["history"][1]["to_state"] == "TASKS"
