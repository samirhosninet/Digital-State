import json
import os
from typing import Dict, Any, List

from digital_state.core.registry import Agent
from digital_state.core.exceptions import GovernanceError


class PolicyEngine:
    """Configurable Policy Engine evaluating permissions independently from business logic."""

    def __init__(self, policies_path: str = ""):
        self.policies_path = policies_path
        if not self.policies_path:
            # Default lookup in package contracts folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.policies_path = os.path.join(current_dir, "contracts", "policies.json")
        
        self.policy_rules: Dict[str, str] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        """Loads permission rules from external config."""
        if not os.path.exists(self.policies_path):
            raise GovernanceError(f"Policy configuration file not found at '{self.policies_path}'.")

        try:
            with open(self.policies_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.policy_rules = data.get("rules", {})
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed policies config JSON at '{self.policies_path}': {e}") from e

    def evaluate(self, agent: Agent, action: str, context: Dict[str, Any] = None) -> bool:
        """Evaluate if an agent is permitted to perform an action under a given context."""
        if agent.status != "Active":
            return False

        # Determine required permission for the action
        required_permission = self.policy_rules.get(action)
        if not required_permission:
            # Check context overrides or custom rules
            if context and "custom_permission" in context:
                required_permission = context["custom_permission"]
            else:
                raise GovernanceError(f"No policy defined for action '{action}'.")

        # Check if the agent possesses the required permission
        return required_permission in agent.permissions
