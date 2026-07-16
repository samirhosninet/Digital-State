import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import LifecycleError, RegistryError, EvidenceError
from tests.conftest import sign_payload


def test_planning_gate_unit_rules():
    """Verify that submit_planning_evidence and lifecycle gate validations assert correct rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-planning-unit"

        # Initially in SPECIFICATION state - planning evidence submission must fail
        with pytest.raises(LifecycleError) as exc:
            kernel.submit_planning_evidence(
                feature_id=feature_id,
                agent_id="builder-agent",
                plan_file="specs/001-plan.md",
                technical_context_complete=True,
                signature="sig",
            )
        assert "Cannot submit 'PLANNING' evidence in state 'SPECIFICATION'" in str(exc.value)

        # Transition feature to PLANNING state first
        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 2}
        spec_sig = sign_payload("prime", spec_content)
        
        kernel.submit_spec_evidence(
            feature_id=feature_id,
            agent_id="prime-agent",
            spec_file="specs/001-spec.md",
            requirements_count=2,
            signature=spec_sig,
        )
        kernel.approve_gate(feature_id, "SPECIFICATION", "auditor-agent")
        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # Now in PLANNING state - invalid signature must fail
        with pytest.raises(EvidenceError):
            kernel.submit_planning_evidence(
                feature_id=feature_id,
                agent_id="builder-agent",
                plan_file="specs/001-plan.md",
                technical_context_complete=True,
                signature="invalid-sig",
            )

        # Non-compliant contract (technical_context_complete is False) must fail
        bad_plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": False}
        bad_plan_sig = sign_payload("builder", bad_plan_content)

        with pytest.raises(EvidenceError) as exc:
            kernel.submit_planning_evidence(
                feature_id=feature_id,
                agent_id="builder-agent",
                plan_file="specs/001-plan.md",
                technical_context_complete=False,
                signature=bad_plan_sig,
            )
        assert "field 'technical_context_complete' must equal 'True'" in str(exc.value)
