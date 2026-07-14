import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import LifecycleError, RegistryError, EvidenceError


def setup_spec_and_transition(kernel: GovernanceKernel, feature_id: str) -> None:
    """Helper utility to initialize a feature and transition it to PLANNING."""
    spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
    serialized = json.dumps(spec_content, sort_keys=True)
    import hashlib
    spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    spec_sig = f"key-prime-signed-{spec_hash}"
    
    kernel.submit_spec_evidence(
        feature_id=feature_id,
        agent_id="prime-agent",
        spec_file="specs/001-spec.md",
        requirements_count=3,
        signature=spec_sig,
    )


def test_story2_planning_gate_approval_success():
    """Verify Auditor can approve conforming plan, transitioning state to TASKS and generating logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-plan-success"

        # Start and move to PLANNING
        setup_spec_and_transition(kernel, feature_id)
        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # Builder signs valid planning evidence
        content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        serialized = json.dumps(content, sort_keys=True)
        import hashlib
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        builder_sig = f"key-builder-signed-{content_hash}"

        kernel.submit_planning_evidence(
            feature_id=feature_id,
            agent_id="builder-agent",
            plan_file="specs/001-plan.md",
            technical_context_complete=True,
            signature=builder_sig,
        )

        # Auditor approves transition
        kernel.approve_plan(feature_id=feature_id, agent_id="auditor-agent")
        
        # State transitions to TASKS
        assert kernel.get_feature_state(feature_id) == "TASKS"

        # Check logs are generated for both submit and transition
        assert kernel.verify_integrity() is True
        logs = kernel.audit_logger.read_entries()
        # 4 logs: 1. SUBMIT SPEC, 2. SPEC transition, 3. Submit planning evidence, 4. PLAN transition
        assert len(logs) == 4
        assert logs[2]["event_type"] == "SUBMIT_EVIDENCE"
        assert logs[3]["event_type"] == "STATE_TRANSITION"
        assert logs[3]["details"]["to_state"] == "TASKS"


def test_story2_planning_gate_rejection_path():
    """Verify Auditor rejection invalidates the gate and prevents state transition."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-plan-rejection"

        setup_spec_and_transition(kernel, feature_id)

        # Builder submits conforming evidence
        content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        serialized = json.dumps(content, sort_keys=True)
        import hashlib
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        builder_sig = f"key-builder-signed-{content_hash}"

        kernel.submit_planning_evidence(
            feature_id=feature_id,
            agent_id="builder-agent",
            plan_file="specs/001-plan.md",
            technical_context_complete=True,
            signature=builder_sig,
        )

        # Auditor vetoes the planning gate
        kernel.reject_plan(feature_id=feature_id, agent_id="auditor-agent")

        # Trying to transition to TASKS now must fail since validation is cleared
        with pytest.raises(LifecycleError) as exc:
            kernel.approve_plan(feature_id=feature_id, agent_id="auditor-agent")
        assert "validation for state 'PLANNING' has not been satisfied" in str(exc.value)

        # Verify state remains PLANNING
        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # Check logs contain veto
        assert kernel.verify_integrity() is True
        logs = kernel.audit_logger.read_entries()
        assert logs[-1]["event_type"] == "GATE_VETO"
        assert logs[-1]["details"]["reason"] == "Auditor rejected planning evidence."


def test_story2_planning_gate_unauthorized_attempt():
    """Verify unauthorized agents cannot approve state transitions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-plan-unauth"

        setup_spec_and_transition(kernel, feature_id)

        # Submit plan
        content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        serialized = json.dumps(content, sort_keys=True)
        import hashlib
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        builder_sig = f"key-builder-signed-{content_hash}"

        kernel.submit_planning_evidence(
            feature_id=feature_id,
            agent_id="builder-agent",
            plan_file="specs/001-plan.md",
            technical_context_complete=True,
            signature=builder_sig,
        )

        # Prime agent tries to approve (unauthorized action mapping)
        with pytest.raises(LifecycleError) as exc:
            kernel.approve_plan(feature_id=feature_id, agent_id="prime-agent")
        assert "is not authorized" in str(exc.value)

        # State must remain PLANNING
        assert kernel.get_feature_state(feature_id) == "PLANNING"
