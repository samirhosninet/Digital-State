import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import RegistryError, EvidenceError, LifecycleError
from tests.conftest import sign_payload


def test_story1_specification_gate_success():
    """Verify that a registered Prime agent can submit valid specification evidence and transition to PLANNING."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Scaffold specify folder
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        # Initialize kernel without bootstrap checks for unit setup
        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-us1-001"

        # Check initial state
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"

        # Generate a real ECDSA P-256 signature from the Prime identity
        content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        valid_signature = sign_payload("prime", content)

        # Submit valid evidence
        kernel.submit_spec_evidence(
            feature_id=feature_id,
            agent_id="prime-agent",
            spec_file="specs/001-spec.md",
            requirements_count=3,
            signature=valid_signature,
        )
        kernel.approve_gate(feature_id, "SPECIFICATION", "auditor-agent")

        # State must transition to PLANNING
        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # Verify audit log contains transition
        assert kernel.verify_integrity() is True
        logs = kernel.audit_logger.read_entries()
        # 3 entries: 1. SUBMIT_EVIDENCE, 2. STATE_TRANSITION (to PLANNING),
        # 3. AUTHORIZATION_GRANTED from the independent auditor approval.
        assert len(logs) == 3
        assert logs[1]["event_type"] == "STATE_TRANSITION"
        assert logs[1]["details"]["to_state"] == "PLANNING"
        assert logs[2]["event_type"] == "AUTHORIZATION_GRANTED"


def test_story1_specification_gate_failures():
    """Verify that unauthorized requests, invalid signatures, and non-compliant requirements are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-us1-failed"

        # 1. Builder agent CAN submit specification evidence (spec 009 allows ANY
        #    agent to SUBMIT), but CANNOT independently approve the gate.
        content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        builder_sig = sign_payload("builder", content)

        # Submit succeeds for the builder agent.
        kernel.submit_spec_evidence(
            feature_id=feature_id,
            agent_id="builder-agent",
            spec_file="specs/001-spec.md",
            requirements_count=3,
            signature=builder_sig,
        )
        # Builder submitted evidence but state must remain SPECIFICATION until an
        # independent approver transitions it.
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"

        # Builder cannot self-approve: independent (auditor) approval is required.
        with pytest.raises(LifecycleError) as exc_info:
            kernel.approve_gate(feature_id, "SPECIFICATION", "builder-agent")
        assert "cannot approve gate" in str(exc_info.value)
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"

        # 2. Invalid signature
        with pytest.raises(EvidenceError) as exc_info:
            kernel.submit_spec_evidence(
                feature_id=feature_id,
                agent_id="prime-agent",
                spec_file="specs/001-spec.md",
                requirements_count=3,
                signature="invalid-signature-value",
            )
        assert "signature" in str(exc_info.value).lower()
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"

        # 3. Non-compliant contract (requirements_count must be >= 1)
        # Re-generate prime signature with low requirements_count
        bad_content = {"spec_file": "specs/001-spec.md", "requirements_count": 0}
        bad_prime_sig = sign_payload("prime", bad_content)

        with pytest.raises(EvidenceError) as exc_info:
            kernel.submit_spec_evidence(
                feature_id=feature_id,
                agent_id="prime-agent",
                spec_file="specs/001-spec.md",
                requirements_count=0,
                signature=bad_prime_sig,
            )
        assert "field 'requirements_count' must be >= 1" in str(exc_info.value)
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"
