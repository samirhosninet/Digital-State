import os
import tempfile
import json
import pytest

from kernel.engine import GovernanceKernel
from kernel.exceptions import LifecycleError, RegistryError, EvidenceError


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
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
        
        kernel.submit_spec_evidence(
            feature_id=feature_id,
            agent_id="prime-agent",
            spec_file="specs/001-spec.md",
            requirements_count=2,
            signature=spec_sig,
        )
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
        bad_plan_serialized = json.dumps(bad_plan_content, sort_keys=True)
        bad_plan_hash = hashlib.sha256(bad_plan_serialized.encode("utf-8")).hexdigest()
        bad_plan_sig = f"key-builder-signed-{bad_plan_hash}"

        with pytest.raises(EvidenceError) as exc:
            kernel.submit_planning_evidence(
                feature_id=feature_id,
                agent_id="builder-agent",
                plan_file="specs/001-plan.md",
                technical_context_complete=False,
                signature=bad_plan_sig,
            )
        assert "field 'technical_context_complete' must equal 'True'" in str(exc.value)
