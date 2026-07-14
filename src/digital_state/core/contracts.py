import json
import os
from typing import Dict, Any, List

from digital_state.core.exceptions import EvidenceError, GovernanceError
from digital_state.core.evidence import Evidence


class ContractEngine:
    """Loads and dynamically evaluates gate contracts from declarative JSON rules."""

    def __init__(self, contracts_root: str):
        self.contracts_root = contracts_root
        self.evidence_gate_dir = os.path.join(self.contracts_root, "evidence_gate")
        self.audit_gate_dir = os.path.join(self.contracts_root, "audit_gate")

    def _load_contract(self, dir_path: str, gate_type: str) -> Dict[str, Any]:
        """Loads a contract schema file."""
        contract_path = os.path.join(dir_path, f"{gate_type.lower()}.json")
        if not os.path.exists(contract_path):
            raise GovernanceError(f"Contract not defined for gate type '{gate_type}' at {contract_path}.")

        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed contract schema at '{contract_path}': {e}") from e

    def _evaluate_rules(self, rules: List[Dict[str, Any]], content: Dict[str, Any], gate_type: str) -> None:
        """Dynamically evaluates rule operators on the evidence content."""
        for rule in rules:
            field = rule.get("field")
            operator = rule.get("operator")
            target_value = rule.get("value")

            if not field or not operator:
                raise GovernanceError("Malformed contract rule: must specify field and operator.")

            # Operator: exists
            if operator == "exists":
                if field not in content:
                    raise EvidenceError(f"Evidence missing required field '{field}' for gate '{gate_type}'.")

            # Operator: gte
            elif operator == "gte":
                actual_value = content.get(field)
                if actual_value is None:
                    raise EvidenceError(f"Evidence missing required comparison field '{field}' for gate '{gate_type}'.")
                
                try:
                    if float(actual_value) < float(target_value):
                        raise EvidenceError(
                            f"Evidence validation failed: field '{field}' must be >= {target_value}, got {actual_value}."
                        )
                except (ValueError, TypeError) as e:
                    raise EvidenceError(
                        f"Type comparison error for field '{field}' against target '{target_value}': {e}"
                    ) from e

            # Operator: eq
            elif operator == "eq":
                actual_value = content.get(field)
                if actual_value != target_value:
                    raise EvidenceError(
                        f"Evidence validation failed: field '{field}' must equal '{target_value}', got '{actual_value}'."
                    )
            
            else:
                raise GovernanceError(f"Unsupported contract operator '{operator}' defined in gate rules.")

    def validate_evidence_gate(self, gate_type: str, evidence: Evidence) -> bool:
        """Validates that a piece of evidence complies with the corresponding evidence gate contract rules."""
        contract = self._load_contract(self.evidence_gate_dir, gate_type)
        rules = contract.get("rules", [])
        self._evaluate_rules(rules, evidence.content, gate_type)
        return True

    def validate_audit_gate(self, gate_type: str, audit_data: Dict[str, Any]) -> bool:
        """Validates that audit metadata complies with the corresponding audit gate contract rules."""
        contract = self._load_contract(self.audit_gate_dir, gate_type)
        rules = contract.get("rules", [])
        self._evaluate_rules(rules, audit_data, gate_type)
        return True
