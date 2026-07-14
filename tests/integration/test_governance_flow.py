import os
import tempfile
import json
import pytest

from digital_state.core.registry import AgentRegistry
from digital_state.core.evidence import Evidence
from digital_state.core.policy import PolicyEngine
from digital_state.core.contracts import ContractEngine
from digital_state.core.lifecycle import LifecycleEngine
from digital_state.core.audit import AuditLogger
from digital_state.core.bootstrap import BootstrapValidator
from digital_state.core.exceptions import LifecycleError, EvidenceError


def test_end_to_end_governance_flow(shared_contracts_dir):
    """End-to-End integration test simulating the entire SpecKit workflow transition gates.
    
    This flows from SPECIFICATION -> PLANNING -> TASKS -> IMPLEMENTATION -> VERIFICATION -> COMPLETED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Setup workspace mockup files for bootstrap
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes", "version": "0.12.15.dev0"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential", "integration": "hermes"}, f)

        # 2. Initialize core components
        registry = AgentRegistry(os.path.join(specify_dir, "agents.json"))
        audit_logger = AuditLogger(os.path.join(specify_dir, "memory", "audit_log.jsonl"))
        policy_engine = PolicyEngine()
        contract_engine = ContractEngine(shared_contracts_dir)
        lifecycle = LifecycleEngine()

        # 3. Verify Bootstrap (Mocking environment availability checks)
        bootstrap = BootstrapValidator(workspace_root=tmpdir)
        with patch_bootstrap_environment(bootstrap):
            bootstrap.run_bootstrap()

        # Feature starts in SPECIFICATION state
        feature_id = "feat-sdd-001"
        assert lifecycle.get_state(feature_id) == "SPECIFICATION"

        # --- STEP A: SPECIFICATION -> PLANNING (Authorized by Prime) ---
        # Prime submits spec evidence matching contract: requirements_count >= 1, spec_file present
        spec_evidence = Evidence(
            evidence_id="ev-spec",
            owner="prime-agent",
            evidence_type="SPECIFICATION",
            content={"spec_file": "specs/001-spec.md", "requirements_count": 3},
            signature="sig",
        )
        assert lifecycle.validate_gate(feature_id, "SPECIFICATION", spec_evidence, contract_engine) is True

        lifecycle.transition(
            feature_id=feature_id,
            next_state="PLANNING",
            agent_id="prime-agent",
            registry=registry,
            policy_engine=policy_engine,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state(feature_id) == "PLANNING"

        # --- STEP B: PLANNING -> TASKS (Authorized by Auditor) ---
        # Builder submits planning evidence
        plan_evidence = Evidence(
            evidence_id="ev-plan",
            owner="builder-agent",
            evidence_type="PLANNING",
            content={"plan_file": "specs/001-plan.md", "technical_context_complete": True},
            signature="sig",
        )
        assert lifecycle.validate_gate(feature_id, "PLANNING", plan_evidence, contract_engine) is True

        lifecycle.transition(
            feature_id=feature_id,
            next_state="TASKS",
            agent_id="auditor-agent",
            registry=registry,
            policy_engine=policy_engine,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state(feature_id) == "TASKS"

        # --- STEP C: TASKS -> IMPLEMENTATION (Authorized by Auditor) ---
        # Builder submits tasks list (represented as planning gate audit results here)
        # Note: TASKS to IMPLEMENTATION requires validating the planning checklist contract
        planning_audit = {
            "checklist_file": "checklists/requirements.md",
            "checks_pass": True
        }
        assert contract_engine.validate_audit_gate("PLANNING", planning_audit) is True

        # Register task gate validation in lifecycle
        tasks_evidence = Evidence(
            evidence_id="ev-tasks",
            owner="builder-agent",
            evidence_type="TASKS",
            content={"tasks_file": "specs/001-tasks.md", "tasks_count": 21, "requirements_count": 21},
            signature="sig",
        )
        lifecycle.validate_gate(feature_id, "TASKS", tasks_evidence, contract_engine)

        lifecycle.transition(
            feature_id=feature_id,
            next_state="IMPLEMENTATION",
            agent_id="auditor-agent",
            registry=registry,
            policy_engine=policy_engine,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state(feature_id) == "IMPLEMENTATION"

        # --- STEP D: IMPLEMENTATION -> VERIFICATION (Authorized by Auditor) ---
        # Builder completes all tasks and submits evidence matching implementation contract
        impl_evidence = Evidence(
            evidence_id="ev-impl",
            owner="builder-agent",
            evidence_type="IMPLEMENTATION",
            content={"tasks_file": "specs/001-tasks.md", "all_tasks_completed": True},
            signature="sig",
        )
        assert lifecycle.validate_gate(feature_id, "IMPLEMENTATION", impl_evidence, contract_engine) is True

        lifecycle.transition(
            feature_id=feature_id,
            next_state="VERIFICATION",
            agent_id="auditor-agent",
            registry=registry,
            policy_engine=policy_engine,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state(feature_id) == "VERIFICATION"

        # --- STEP E: VERIFICATION -> COMPLETED (Authorized by Prime) ---
        # Verification audit gate validated: walkthrough completes, tests pass
        verification_audit = {
            "walkthrough_file": "walkthrough.md",
            "all_tests_passed": True
        }
        assert contract_engine.validate_audit_gate("VERIFICATION", verification_audit) is True

        # Register verification validation in lifecycle
        verification_evidence = Evidence(
            evidence_id="ev-verification",
            owner="auditor-agent",
            evidence_type="VERIFICATION",
            content={"walkthrough_file": "walkthrough.md", "all_tests_passed": True},
            signature="sig",
        )
        lifecycle.validate_gate(feature_id, "VERIFICATION", verification_evidence, contract_engine)

        lifecycle.transition(
            feature_id=feature_id,
            next_state="COMPLETED",
            agent_id="prime-agent",
            registry=registry,
            policy_engine=policy_engine,
            audit_logger=audit_logger,
        )
        assert lifecycle.get_state(feature_id) == "COMPLETED"

        # Verify audit log integrity
        assert audit_logger.verify_log_integrity() is True
        log_entries = audit_logger.read_entries()
        assert len(log_entries) == 5  # Five transitions logged
        assert log_entries[0]["details"]["to_state"] == "PLANNING"
        assert log_entries[4]["details"]["to_state"] == "COMPLETED"


def patch_bootstrap_environment(bootstrap: BootstrapValidator):
    """Utility mock to patch external binaries checks for testing."""
    import unittest.mock as mock
    m1 = mock.patch.object(bootstrap, "verify_hermes_availability", return_value=True)
    m2 = mock.patch.object(bootstrap, "verify_speckit_availability", return_value=True)
    m3 = mock.patch.object(bootstrap, "verify_runtime_adapter_readiness", return_value=True)
    
    class MultiPatch:
        def __enter__(self):
            m1.__enter__()
            m2.__enter__()
            m3.__enter__()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            m1.__exit__(exc_type, exc_val, exc_tb)
            m2.__exit__(exc_type, exc_val, exc_tb)
            m3.__exit__(exc_type, exc_val, exc_tb)
            
    return MultiPatch()
