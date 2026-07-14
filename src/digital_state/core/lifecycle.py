import json
import os
from typing import Dict, Any, List

from digital_state.core.exceptions import LifecycleError, RegistryError, GovernanceError
from digital_state.core.registry import AgentRegistry
from digital_state.core.policy import PolicyEngine
from digital_state.core.audit import AuditLogger
from digital_state.core.evidence import Evidence
from digital_state.core.contracts import ContractEngine


class LifecycleEngine:
    """Enforces transitions and validation gates from external lifecycle configurations."""

    def __init__(self, config_path: str = "", state_path: str = ""):
        self.config_path = config_path
        self.state_path = state_path
        
        if not self.config_path:
            # Default lookup in package contracts folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(current_dir, "contracts", "lifecycle.json")

        self.phases: List[str] = []
        self.transitions: Dict[str, Dict[str, str]] = {}
        
        self.feature_states: Dict[str, str] = {}
        self.gate_validations: Dict[str, Dict[str, bool]] = {}
        
        self._load_config()
        self._load_state()

    def _load_config(self) -> None:
        """Load states and transitions map from config."""
        if not os.path.exists(self.config_path):
            raise GovernanceError(f"Lifecycle configuration file not found at '{self.config_path}'.")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.phases = data.get("phases", [])
                self.transitions = data.get("transitions", {})
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed lifecycle config JSON at '{self.config_path}': {e}") from e

    def _load_state(self) -> None:
        """Loads feature states and validations from the persistence file if it exists."""
        if not self.state_path or not os.path.exists(self.state_path):
            return

        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.feature_states = data.get("feature_states", {})
                self.gate_validations = data.get("gate_validations", {})
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback to empty memory state if file is corrupted
            pass

    def _save_state(self) -> None:
        """Saves current feature states and validation gates to the persistence file atomically."""
        if not self.state_path:
            return

        tmp_path = self.state_path + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            data = {
                "feature_states": self.feature_states,
                "gate_validations": self.gate_validations,
            }
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.state_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise GovernanceError(f"Failed to write lifecycle state persistence file: {e}") from e

    def get_state(self, feature_id: str) -> str:
        """Returns the current state of a feature. Defaults to first phase."""
        if not self.phases:
            raise LifecycleError("Lifecycle phases configuration is empty.")
        return self.feature_states.get(feature_id, self.phases[0])

    def can_transition(
        self,
        feature_id: str,
        next_state: str,
        agent_id: str,
        registry: AgentRegistry,
        policy_engine: PolicyEngine,
    ) -> bool:
        """Evaluates transition rules against the policy engine and phase order constraints."""
        current_state = self.get_state(feature_id)
        
        # Verify next state exists
        if next_state not in self.phases:
            raise LifecycleError(f"Requested state '{next_state}' is not defined in configuration.")

        # Check configured transition rules
        transition_rule = self.transitions.get(next_state)
        if not transition_rule:
            return False

        # Verify from_state matches current state
        if transition_rule.get("from") != current_state:
            return False

        # Load agent and verify status and policy permissions
        agent = registry.get_agent(agent_id)
        if not agent:
            raise RegistryError(f"Agent '{agent_id}' is not registered.")
        
        if agent.status != "Active":
            return False

        # Retrieve action permission required by the transition configuration
        required_action = transition_rule.get("required_action")
        if not required_action:
            raise LifecycleError(f"Transition to '{next_state}' lacks required_action definition.")

        return policy_engine.evaluate(agent, required_action)

    def validate_gate(
        self,
        feature_id: str,
        state: str,
        evidence: Evidence,
        contract_engine: ContractEngine,
    ) -> bool:
        """Validates that a transition gate's contract criteria have been satisfied by evidence."""
        is_valid = contract_engine.validate_evidence_gate(state, evidence)
        if is_valid:
            if feature_id not in self.gate_validations:
                self.gate_validations[feature_id] = {}
            self.gate_validations[feature_id][state] = True
            self._save_state()
        return is_valid

    def transition(
        self,
        feature_id: str,
        next_state: str,
        agent_id: str,
        registry: AgentRegistry,
        policy_engine: PolicyEngine,
        audit_logger: AuditLogger,
    ) -> None:
        """Executes a state transition if permitted and if the corresponding gate has been validated."""
        current_state = self.get_state(feature_id)
        
        # 1. Check permission and ordering
        if not self.can_transition(feature_id, next_state, agent_id, registry, policy_engine):
            raise LifecycleError(
                f"Transition from '{current_state}' to '{next_state}' is not authorized for Agent '{agent_id}'."
            )

        # 2. Check that the gate validation for the current state has been registered
        if next_state != self.phases[0]:
            validated = self.gate_validations.get(feature_id, {}).get(current_state, False)
            if not validated:
                raise LifecycleError(
                    f"Transition from '{current_state}' to '{next_state}' is blocked: "
                    f"Gate validation for state '{current_state}' has not been satisfied."
                )

        # 3. Apply state transition
        self.feature_states[feature_id] = next_state
        self._save_state()
        
        # 4. Log the event immutably
        audit_logger.append_entry(
            event_type="STATE_TRANSITION",
            agent_id=agent_id,
            details={
                "feature_id": feature_id,
                "from_state": current_state,
                "to_state": next_state,
            },
        )
