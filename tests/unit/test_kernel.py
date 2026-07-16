import os
import tempfile
import json
import pytest
from unittest.mock import patch

from digital_state.core.registry import AgentRegistry, Agent
from digital_state.core.evidence import Evidence
from digital_state.core.policy import PolicyEngine
from digital_state.core.contracts import ContractEngine
from digital_state.core.lifecycle import LifecycleEngine
from integrations.hermes.client import HermesClient
from digital_state.core.bootstrap import BootstrapValidator
from digital_state.core.audit import AuditLogger
from digital_state.core.exceptions import (
    RegistryError,
    EvidenceError,
    LifecycleError,
    GovernanceError,
)
from digital_state.core.engine import GovernanceKernel
from tests.conftest import content_hash, public_key_dict, sign_payload


def test_agent_registry():
    """Verify registry loads baseline profiles and restricts duplicate registrations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        reg_file = os.path.join(tmpdir, "agents.json")
        registry = AgentRegistry(reg_file)

        # Check default registrations
        prime = registry.get_agent("prime-agent")
        assert prime is not None
        assert prime.role == "Prime"
        assert "define_goals" in prime.permissions

        # Register custom profile
        custom = registry.register_agent(
            agent_id="custom-agent",
            role="QA",
            permissions=["veto_gate"],
            public_key=public_key_dict("builder"),
        )
        assert registry.get_agent("custom-agent").role == "QA"

        # Duplicate register must fail
        with pytest.raises(RegistryError):
            registry.register_agent("prime-agent", "Prime", [])


def test_evidence_verification():
    """Verify evidence model hashes content and verifies a real ECDSA signature."""
    content = {"spec_file": "specs/001-spec.md", "requirements_count": 5}

    correct_sig = sign_payload("prime", content)

    evidence = Evidence(
        evidence_id="ev-001",
        owner="prime-agent",
        evidence_type="SPECIFICATION",
        content=content,
        signature=correct_sig,
    )

    assert evidence.hash == content_hash(content)
    assert evidence.verify_signature(public_key_dict("prime")) is True

    # Tampered content must fail verification
    tampered = Evidence(
        evidence_id="ev-001",
        owner="prime-agent",
        evidence_type="SPECIFICATION",
        content={"spec_file": "specs/001-spec.md", "requirements_count": 999},
        signature=correct_sig,
    )
    with pytest.raises(EvidenceError):
        tampered.verify_signature(public_key_dict("prime"))


def test_policy_engine():
    """Verify policy engine decouples permissions evaluation from business logic."""
    policy = PolicyEngine()
    
    prime = Agent("prime", "Prime", ["define_goals", "sign_off_spec"])
    builder = Agent("builder", "Builder", ["submit_plan"], status="Active")
    suspended_builder = Agent("builder-2", "Builder", ["submit_plan"], status="Suspended")

    # Positive evaluation
    assert policy.evaluate(prime, "define_goals") is True
    assert policy.evaluate(builder, "submit_plan") is True

    # Suspended agent fails evaluation
    assert policy.evaluate(suspended_builder, "submit_plan") is False

    # Unauthorized action evaluation
    assert policy.evaluate(builder, "define_goals") is False


def test_contract_engine(shared_contracts_dir):
    """Verify ContractEngine loads JSON schemas and validates evidence gates."""
    engine = ContractEngine(shared_contracts_dir)

    # Valid evidence matching specification.json contract
    valid_spec_evidence = Evidence(
        evidence_id="ev-spec",
        owner="prime-agent",
        evidence_type="SPECIFICATION",
        content={"spec_file": "specs/001-spec.md", "requirements_count": 2},
        signature="sig",
    )
    assert engine.validate_evidence_gate("SPECIFICATION", valid_spec_evidence) is True

    # Invalid evidence (missing spec_file) must fail contract validation
    invalid_spec_evidence = Evidence(
        evidence_id="ev-spec-invalid",
        owner="prime-agent",
        evidence_type="SPECIFICATION",
        content={"requirements_count": 2},
        signature="sig",
    )
    with pytest.raises(EvidenceError) as exc:
        engine.validate_evidence_gate("SPECIFICATION", invalid_spec_evidence)
    assert "missing required field 'spec_file'" in str(exc.value)

    # Invalid evidence (requirements_count too low) must fail contract validation
    low_req_evidence = Evidence(
        evidence_id="ev-spec-low",
        owner="prime-agent",
        evidence_type="SPECIFICATION",
        content={"spec_file": "specs/001-spec.md", "requirements_count": 0},
        signature="sig",
    )
    with pytest.raises(EvidenceError) as exc:
        engine.validate_evidence_gate("SPECIFICATION", low_req_evidence)
    assert "field 'requirements_count' must be >= 1" in str(exc.value)


def test_lifecycle_transitions(shared_contracts_dir):
    """Verify LifecycleEngine restricts transitions to gate validation sequence."""
    lifecycle = LifecycleEngine()
    policy = PolicyEngine()
    contract_engine = ContractEngine(shared_contracts_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        registry = AgentRegistry(os.path.join(tmpdir, "agents.json"))
        audit_logger = AuditLogger(os.path.join(tmpdir, "audit.jsonl"))

        # Feature starts in SPECIFICATION state
        assert lifecycle.get_state("feat-001") == "SPECIFICATION"

        # Prime signs off spec evidence to unlock PLANNING transition
        spec_evidence = Evidence(
            evidence_id="ev-spec",
            owner="prime-agent",
            evidence_type="SPECIFICATION",
            content={"spec_file": "specs/001-spec.md", "requirements_count": 3},
            signature="sig",
        )
        assert lifecycle.validate_gate("feat-001", "SPECIFICATION", spec_evidence, contract_engine) is True

        # Execute transition from SPECIFICATION to PLANNING
        lifecycle.transition(
            feature_id="feat-001",
            next_state="PLANNING",
            agent_id="prime-agent",
            registry=registry,
            policy_engine=policy,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state("feat-001") == "PLANNING"

        # Out-of-order transition (PLANNING -> IMPLEMENTATION, bypassing TASKS) must fail
        with pytest.raises(LifecycleError):
            lifecycle.transition(
                feature_id="feat-001",
                next_state="IMPLEMENTATION",
                agent_id="builder-agent",
                registry=registry,
                policy_engine=policy,
                audit_logger=audit_logger,
            )


def test_hermes_runtime_adapter():
    """Verify HermesClient mock connection is ready and metadata is retrievable."""
    client = HermesClient()
    assert client.metadata()["status"] == "Ready"
    assert client.self_test() is True


def test_submitter_cannot_approve_own_gate():
    """Independent approval is enforced and its denial is retained in the audit log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(os.path.join(specify_dir, "memory"))
        with open(os.path.join(specify_dir, "agents.json"), "w", encoding="utf-8") as f:
            json.dump({
                "builder": {"agent_id": "builder", "role": "Builder", "status": "Active",
                            "permissions": ["submit_evidence"], "public_key": {}},
                "auditor": {"agent_id": "auditor", "role": "Auditor", "status": "Active",
                            "permissions": ["approve_spec"], "public_key": {}},
            }, f)
        with open(os.path.join(specify_dir, "state.json"), "w", encoding="utf-8") as f:
            json.dump({"feature_states": {}, "gate_validations": {"feat": {"SPECIFICATION": True}}}, f)
        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        kernel.audit_logger.append_entry("SUBMIT_EVIDENCE", "builder", {
            "feature_id": "feat", "evidence_type": "SPECIFICATION", "evidence_id": "ev-spec"
        })
        with pytest.raises(LifecycleError, match="cannot approve"):
            kernel.approve_gate("feat", "SPECIFICATION", "builder")
        assert kernel.audit_logger.read_entries()[-1]["event_type"] == "AUTHORIZATION_DENIED"
        kernel.approve_gate("feat", "SPECIFICATION", "auditor")
        assert kernel.get_feature_state("feat") == "PLANNING"
