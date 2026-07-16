import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import LifecycleError, EvidenceError
from tests.conftest import sign_payload


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
        spec_sig = sign_payload("prime", spec_content)
        kernel.submit_spec_evidence(feature_id, "prime-agent", "specs/001-spec.md", 3, spec_sig)
        kernel.approve_gate(feature_id, "SPECIFICATION", "auditor-agent")

        # Submit plan
        plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
        plan_sig = sign_payload("builder", plan_content)
        kernel.submit_planning_evidence(feature_id, "builder-agent", "specs/001-plan.md", True, plan_sig)
        
        # Approve and transition to TASKS
        kernel.approve_plan(feature_id, "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "TASKS"

        # Now in TASKS: Submit invalid tasks evidence (tasks_count is 0, which is < 1)
        bad_tasks = {"tasks_file": "specs/001-tasks.md", "tasks_count": 0, "requirements_count": 3}
        bad_tasks_sig = sign_payload("builder", bad_tasks)

        with pytest.raises(EvidenceError) as exc:
            kernel.submit_evidence(feature_id, "TASKS", bad_tasks, "builder-agent", bad_tasks_sig)
        assert "field 'tasks_count' must be >= 1" in str(exc.value)

        # Submit valid tasks evidence
        ok_tasks = {"tasks_file": "specs/001-tasks.md", "tasks_count": 21, "requirements_count": 21}
        ok_tasks_sig = sign_payload("builder", ok_tasks)
        kernel.submit_evidence(feature_id, "TASKS", ok_tasks, "builder-agent", ok_tasks_sig)

        # Auditor approves tasks transition to IMPLEMENTATION
        kernel.approve_gate(feature_id, "TASKS", "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "IMPLEMENTATION"
