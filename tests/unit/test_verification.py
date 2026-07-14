import os
import tempfile
import json
import pytest

from kernel.engine import GovernanceKernel
from kernel.exceptions import LifecycleError, EvidenceError


def test_verification_gates_unit_rules():
    """Verify that tasks, implementation, and verification evidence satisfy gate contracts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-verification-unit"

        # Initialize to PLANNING
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
        kernel.submit_spec_evidence(feature_id, "prime-agent", "specs/001-spec.md", 3, spec_sig)

        # Submit plan
        plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        plan_serialized = json.dumps(plan_content, sort_keys=True)
        plan_hash = hashlib.sha256(plan_serialized.encode("utf-8")).hexdigest()
        plan_sig = f"key-builder-signed-{plan_hash}"
        kernel.submit_planning_evidence(feature_id, "builder-agent", "specs/001-plan.md", True, plan_sig)
        
        # Approve and transition to TASKS
        kernel.approve_plan(feature_id, "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "TASKS"

        # Now in TASKS: Submit invalid tasks evidence (tasks_count is 0, which is < 1)
        bad_tasks = {"tasks_file": "specs/001-tasks.md", "tasks_count": 0, "requirements_count": 3}
        bad_tasks_serialized = json.dumps(bad_tasks, sort_keys=True)
        bad_tasks_hash = hashlib.sha256(bad_tasks_serialized.encode("utf-8")).hexdigest()
        bad_tasks_sig = f"key-builder-signed-{bad_tasks_hash}"

        with pytest.raises(EvidenceError) as exc:
            kernel.submit_evidence(feature_id, "TASKS", bad_tasks, "builder-agent", bad_tasks_sig)
        assert "field 'tasks_count' must be >= 1" in str(exc.value)

        # Submit valid tasks evidence
        ok_tasks = {"tasks_file": "specs/001-tasks.md", "tasks_count": 21, "requirements_count": 21}
        ok_tasks_serialized = json.dumps(ok_tasks, sort_keys=True)
        ok_tasks_hash = hashlib.sha256(ok_tasks_serialized.encode("utf-8")).hexdigest()
        ok_tasks_sig = f"key-builder-signed-{ok_tasks_hash}"
        kernel.submit_evidence(feature_id, "TASKS", ok_tasks, "builder-agent", ok_tasks_sig)

        # Auditor approves tasks transition to IMPLEMENTATION
        kernel.approve_gate(feature_id, "TASKS", "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "IMPLEMENTATION"
