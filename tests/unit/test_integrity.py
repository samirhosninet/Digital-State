import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import LifecycleError, EvidenceError


def test_duplicate_and_rollback_prevention():
    """Verify that duplicate approvals, duplicate transitions, and rollbacks are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-integrity-test"

        # 1. SPECIFICATION -> PLANNING
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
        kernel.submit_spec_evidence(feature_id, "prime-agent", "specs/001-spec.md", 3, spec_sig)

        # 2. Try duplicate transition to PLANNING (should fail because current state is PLANNING)
        with pytest.raises(LifecycleError):
            kernel.lifecycle_engine.transition(
                feature_id=feature_id,
                next_state="PLANNING",
                agent_id="prime-agent",
                registry=kernel.registry,
                policy_engine=kernel.policy_engine,
                audit_logger=kernel.audit_logger,
            )

        # 3. Submit planning evidence
        plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        plan_serialized = json.dumps(plan_content, sort_keys=True)
        plan_hash = hashlib.sha256(plan_serialized.encode("utf-8")).hexdigest()
        builder_sig = f"key-builder-signed-{plan_hash}"
        kernel.submit_planning_evidence(feature_id, "builder-agent", "specs/001-plan.md", True, builder_sig)

        # 4. Approve transition to TASKS
        kernel.approve_plan(feature_id, "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "TASKS"

        # 5. Try duplicate approval of planning gate (should fail because state is already TASKS)
        with pytest.raises(LifecycleError):
            kernel.approve_plan(feature_id, "auditor-agent")

        # 6. Try rollback (transition TASKS -> PLANNING)
        with pytest.raises(LifecycleError):
            kernel.lifecycle_engine.transition(
                feature_id=feature_id,
                next_state="PLANNING",
                agent_id="auditor-agent",
                registry=kernel.registry,
                policy_engine=kernel.policy_engine,
                audit_logger=kernel.audit_logger,
            )


def test_last_record_truncation_detection():
    """Verify that deleting the last transition log is detected by verify_integrity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-truncation"

        # State transition to PLANNING
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
        kernel.submit_spec_evidence(feature_id, "prime-agent", "specs/001-spec.md", 3, spec_sig)

        # Verification must pass originally
        assert kernel.verify_integrity() is True

        # Truncate the transition log from the file on disk
        log_path = kernel.config.get_audit_log_path()
        with open(log_path, "w") as f:
            pass # Truncate file entirely

        # verify_integrity must fail now, detecting that current state is PLANNING but audit log lacks it
        with pytest.raises(EvidenceError) as exc:
            kernel.verify_integrity()
        assert "Log truncation detected" in str(exc.value)
