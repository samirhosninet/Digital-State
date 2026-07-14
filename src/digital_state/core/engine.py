import os
import json
from typing import Dict, Any

from digital_state.core.exceptions import GovernanceError, RegistryError, EvidenceError, LifecycleError
from digital_state.core.config import ConfigManager
from digital_state.core.registry import AgentRegistry, Agent
from digital_state.core.policy import PolicyEngine
from digital_state.core.contracts import ContractEngine
from digital_state.core.lifecycle import LifecycleEngine
from digital_state.core.evidence import Evidence
from digital_state.core.audit import AuditLogger
from digital_state.core.bootstrap import BootstrapValidator
from digital_state.core.locking import FileLock


class GovernanceKernel:
    """The central governance kernel coordinating registry, policy, contract, and lifecycle engines."""

    def __init__(self, workspace_root: str, run_bootstrap: bool = True):
        self.workspace_root = os.path.abspath(workspace_root)
        
        # 1. Initialize Configuration Manager
        self.config = ConfigManager(self.workspace_root)
        
        # 2. Run Bootstrap Validation (can be skipped in tests via run_bootstrap=False)
        if run_bootstrap:
            bootstrap = BootstrapValidator(self.workspace_root)
            bootstrap.run_bootstrap()

        # 3. Instantiate Engine components
        specify_dir = self.config.specify_dir
        self.registry = AgentRegistry(os.path.join(specify_dir, "agents.json"))
        
        # Determine contracts directory relative to the package installation
        current_dir = os.path.dirname(os.path.abspath(__file__))
        contracts_root = os.path.join(current_dir, "contracts")
        self.contract_engine = ContractEngine(contracts_root)
        
        self.policy_engine = PolicyEngine()
        self.lifecycle_engine = LifecycleEngine(state_path=os.path.join(specify_dir, "state.json"))
        
        # Persistent audit trail path resolution
        audit_log_path = self.config.get_audit_log_path()
        self.audit_logger = AuditLogger(audit_log_path)
        self.lock_dir = os.path.join(specify_dir, "governance.lock")

        if run_bootstrap:
            self._recover_stale_lock()
            self.verify_integrity()

    def get_feature_state(self, feature_id: str) -> str:
        """Query the current state of a feature."""
        return self.lifecycle_engine.get_state(feature_id)

    def submit_evidence(
        self,
        feature_id: str,
        gate: str,
        content: Dict[str, Any],
        agent_id: str,
        signature: str,
    ) -> None:
        """Generic endpoint for submitting verifiable gate evidence."""
        with FileLock(self.lock_dir):
            self._submit_evidence_unlocked(feature_id, gate, content, agent_id, signature)

    def _submit_evidence_unlocked(
        self,
        feature_id: str,
        gate: str,
        content: Dict[str, Any],
        agent_id: str,
        signature: str,
    ) -> None:
        current_state = self.get_feature_state(feature_id)
        if current_state != gate:
            raise LifecycleError(f"Cannot submit '{gate}' evidence in state '{current_state}'.")

        agent = self.registry.get_agent(agent_id)
        if not agent:
            raise RegistryError(f"Agent '{agent_id}' is not registered.")

        evidence = Evidence(
            evidence_id=f"ev-{gate.lower()}-{feature_id}",
            owner=agent_id,
            evidence_type=gate,
            content=content,
            signature=signature,
        )

        # Cryptographically verify signature
        evidence.verify_signature(agent.public_key)

        # Validate gate rules using contract engine
        self.lifecycle_engine.validate_gate(
            feature_id=feature_id,
            state=gate,
            evidence=evidence,
            contract_engine=self.contract_engine,
        )

        # Log evidence submission
        self.audit_logger.append_entry(
            event_type="SUBMIT_EVIDENCE",
            agent_id=agent_id,
            details={
                "feature_id": feature_id,
                "evidence_type": gate,
                "evidence_id": evidence.evidence_id,
            }
        )

        # Auto-approve SPECIFICATION sign-off
        if gate == "SPECIFICATION":
            self._approve_gate_unlocked(feature_id, "SPECIFICATION", agent_id)

    def approve_gate(self, feature_id: str, gate: str, agent_id: str) -> None:
        """Generic endpoint to audit and sign off on a gate, transitioning state."""
        with FileLock(self.lock_dir):
            self._approve_gate_unlocked(feature_id, gate, agent_id)

    def _approve_gate_unlocked(self, feature_id: str, gate: str, agent_id: str) -> None:
        current_state = self.get_feature_state(feature_id)
        if current_state != gate:
            raise LifecycleError(f"Cannot approve gate '{gate}' in state '{current_state}'.")

        agent = self.registry.get_agent(agent_id)
        if not agent:
            raise RegistryError(f"Agent '{agent_id}' is not registered.")

        # Find next state from transition map
        next_state = None
        required_action = None
        for n_state, trans in self.lifecycle_engine.transitions.items():
            if trans.get("from") == gate:
                next_state = n_state
                required_action = trans.get("required_action")
                break

        if not next_state or not required_action:
            raise LifecycleError(f"No configured transition exists from state '{gate}'.")

        # Evaluate policy authorization
        if not self.policy_engine.evaluate(agent, required_action):
            raise LifecycleError(f"Agent '{agent_id}' is not authorized to execute transition for action '{required_action}'.")

        # Execute transition
        self.lifecycle_engine.transition(
            feature_id=feature_id,
            next_state=next_state,
            agent_id=agent_id,
            registry=self.registry,
            policy_engine=self.policy_engine,
            audit_logger=self.audit_logger,
        )

    def reject_gate(self, feature_id: str, gate: str, reason: str, agent_id: str) -> None:
        """Generic endpoint to veto a gate, invalidating validation and logging decision."""
        with FileLock(self.lock_dir):
            self._reject_gate_unlocked(feature_id, gate, reason, agent_id)

    def _reject_gate_unlocked(self, feature_id: str, gate: str, reason: str, agent_id: str) -> None:
        current_state = self.get_feature_state(feature_id)
        if current_state != gate:
            raise LifecycleError(f"Cannot reject gate '{gate}' in state '{current_state}'.")

        agent = self.registry.get_agent(agent_id)
        if not agent:
            raise RegistryError(f"Agent '{agent_id}' is not registered.")

        # Verify veto authority
        if not self.policy_engine.evaluate(agent, "veto_gate"):
            raise LifecycleError(f"Agent '{agent_id}' lacks veto authorization.")

        # Invalidate gate validation
        if feature_id in self.lifecycle_engine.gate_validations:
            if gate in self.lifecycle_engine.gate_validations[feature_id]:
                self.lifecycle_engine.gate_validations[feature_id][gate] = False

        # Log veto event
        self.audit_logger.append_entry(
            event_type="GATE_VETO",
            agent_id=agent_id,
            details={
                "feature_id": feature_id,
                "gate_state": gate,
                "reason": reason
            }
        )

    def submit_spec_evidence(
        self,
        feature_id: str,
        agent_id: str,
        spec_file: str,
        requirements_count: int,
        signature: str,
    ) -> None:
        """Submits specification evidence and transitions state to PLANNING."""
        content = {
            "spec_file": spec_file,
            "requirements_count": requirements_count,
        }
        self.submit_evidence(feature_id, "SPECIFICATION", content, agent_id, signature)

    def submit_planning_evidence(
        self,
        feature_id: str,
        agent_id: str,
        plan_file: str,
        technical_context_complete: bool,
        signature: str,
    ) -> None:
        """Builder submits planning evidence."""
        content = {
            "plan_file": plan_file,
            "technical_context_complete": technical_context_complete,
        }
        self.submit_evidence(feature_id, "PLANNING", content, agent_id, signature)

    def approve_plan(self, feature_id: str, agent_id: str) -> None:
        """Auditor approves planning."""
        self.approve_gate(feature_id, "PLANNING", agent_id)

    def reject_plan(self, feature_id: str, agent_id: str) -> None:
        """Auditor rejects planning."""
        self.reject_gate(feature_id, "PLANNING", "Auditor rejected planning evidence.", agent_id)

    def verify_integrity(self) -> bool:
        """Verify the integrity of the audit log chain and check for last-record truncation."""
        # 1. Check chain hashes and indices
        if not self.audit_logger.verify_log_integrity():
            return False

        # 2. Check for truncation: Verify current state matches last transition log
        entries = self.audit_logger.read_entries()
        log_final_states = {}
        for entry in entries:
            if entry.get("event_type") == "STATE_TRANSITION":
                feat_id = entry["details"]["feature_id"]
                to_state = entry["details"]["to_state"]
                log_final_states[feat_id] = to_state

        for feat_id, current_state in self.lifecycle_engine.feature_states.items():
            first_phase = self.lifecycle_engine.phases[0]
            if current_state != first_phase:
                logged_state = log_final_states.get(feat_id)
                if logged_state != current_state:
                    raise EvidenceError(
                        f"Log truncation detected: Feature '{feat_id}' is in state '{current_state}', "
                        f"but audit trail ends at state '{logged_state}'."
                    )

        return True

    def _recover_stale_lock(self) -> None:
        """Checks for stale lock directory on boot and cleans it up."""
        if os.path.exists(self.lock_dir):
            try:
                lock = FileLock(self.lock_dir)
                metadata_path = os.path.join(self.lock_dir, "lock.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pid = data.get("pid")
                    if pid and not lock._is_pid_active(pid):
                        lock.release()
            except Exception:
                pass
