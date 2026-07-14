import os
import tempfile
import json
import pytest
from unittest.mock import patch

from kernel.cli import run_cli
from kernel.engine import GovernanceKernel


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

        # Register custom builder agent via CLI
        code = run_cli([
            "register",
            "--id", "custom-builder",
            "--role", "Builder",
            "--key", "key-custom-builder"
        ], workspace_root=tmpdir)
        assert code == 0
        out, _ = capsys.readouterr()
        assert "registered successfully" in out

        # Submit SPECIFICATION evidence (transitions spec to PLANNING automatically in spec sign-off)
        # Content hash signature for default prime-agent
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
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

        # Check state transitioned to PLANNING
        run_cli(["status", "--feature", feature_id], workspace_root=tmpdir)
        out, _ = capsys.readouterr()
        status_data = json.loads(out)
        assert status_data["current_state"] == "PLANNING"
        assert len(status_data["history"]) == 1
        assert status_data["history"][0]["to_state"] == "PLANNING"

        # 4. Submit PLANNING evidence via custom-builder agent
        plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        plan_serialized = json.dumps(plan_content, sort_keys=True)
        plan_hash = hashlib.sha256(plan_serialized.encode("utf-8")).hexdigest()
        plan_sig = f"key-custom-builder-signed-{plan_hash}"
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
