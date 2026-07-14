import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import RegistryError, EvidenceError, LifecycleError


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

        # Generate a valid signature mock: "{public_key}-signed-{hash}"
        # For 'prime-agent', default public key is 'key-prime'
        content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(content, sort_keys=True)
        import hashlib
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        valid_signature = f"key-prime-signed-{content_hash}"

        # Submit valid evidence
        kernel.submit_spec_evidence(
            feature_id=feature_id,
            agent_id="prime-agent",
            spec_file="specs/001-spec.md",
            requirements_count=3,
            signature=valid_signature,
        )

        # State must transition to PLANNING
        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # Verify audit log contains transition
        assert kernel.verify_integrity() is True
        logs = kernel.audit_logger.read_entries()
        assert len(logs) == 2
        assert logs[1]["details"]["to_state"] == "PLANNING"


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

        # 1. Unauthorized Agent (Builder agent lacks 'sign_off_spec' permission)
        # Generate signature for Builder agent (public key is 'key-builder')
        content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(content, sort_keys=True)
        import hashlib
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        builder_sig = f"key-builder-signed-{content_hash}"

        with pytest.raises(LifecycleError) as exc_info:
            kernel.submit_spec_evidence(
                feature_id=feature_id,
                agent_id="builder-agent",
                spec_file="specs/001-spec.md",
                requirements_count=3,
                signature=builder_sig,
            )
        assert "is not authorized" in str(exc_info.value)
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
        assert "Invalid signature" in str(exc_info.value)
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"

        # 3. Non-compliant contract (requirements_count must be >= 1)
        # Re-generate prime signature with low requirements_count
        bad_content = {"spec_file": "specs/001-spec.md", "requirements_count": 0}
        bad_serialized = json.dumps(bad_content, sort_keys=True)
        bad_hash = hashlib.sha256(bad_serialized.encode("utf-8")).hexdigest()
        bad_prime_sig = f"key-prime-signed-{bad_hash}"

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
