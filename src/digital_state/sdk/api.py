import os
from typing import Dict, Any
from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import GovernanceError

# Semver compatibility range for Hermes plugins targeting this SDK
__sdk_compat_version__ = "^0.1.0"

def is_compatible(plugin_version: str) -> bool:
    """Verifies that a Hermes plugin version matches the SDK's compatibility version."""
    if not plugin_version:
        return False
    # Simple semantic version compatibility check: target version starts with 0.1
    return plugin_version.startswith("0.1.")

def validate_gate_approval(feature_id: str, agent_key: Any, workspace_root: str = None) -> bool:
    """Validates if the agent's key is authorized to approve the current gate transition."""
    root = workspace_root or os.getcwd()
    try:
        kernel = GovernanceKernel(root, run_bootstrap=False)
        
        # Resolve key identifier if passed as a dictionary context from Hermes
        pubkey_str = agent_key
        if isinstance(agent_key, dict):
            pubkey_str = agent_key.get("key_id") or agent_key.get("public_key") or ""
            
        matching_agent = None
        for agent_id, agent in kernel.registry.agents.items():
            if agent.public_key == pubkey_str:
                matching_agent = agent
                break
        if not matching_agent:
            return False
            
        current_state = kernel.get_feature_state(feature_id)
        required_action = None
        for n_state, trans in kernel.lifecycle_engine.transitions.items():
            if trans.get("from") == current_state:
                required_action = trans.get("required_action")
                break
        if not required_action:
            return False
            
        return kernel.policy_engine.evaluate(matching_agent, required_action)
    except Exception:
        return False

def submit_evidence(feature_id: str, gate: str, payload: dict, workspace_root: str = None) -> bool:
    """Submits verifiable gate evidence to the core governance database."""
    root = workspace_root or os.getcwd()
    try:
        kernel = GovernanceKernel(root)
        kernel.submit_evidence(
            feature_id=feature_id,
            gate=gate,
            content=payload.get("content", {}),
            agent_id=payload.get("agent_id"),
            signature=payload.get("signature")
        )
        return True
    except Exception:
        return False

def check_governance_status(feature_id: str, workspace_root: str = None) -> dict:
    """Queries details about the active governance lifecycle state of a feature."""
    root = workspace_root or os.getcwd()
    try:
        kernel = GovernanceKernel(root, run_bootstrap=False)
        state = kernel.get_feature_state(feature_id)
        return {
            "feature_id": feature_id,
            "status": state,
            "validations": kernel.lifecycle_engine.gate_validations.get(feature_id, {})
        }
    except Exception:
        return {"feature_id": feature_id, "status": "UNKNOWN", "validations": {}}

def verify_audit_log(workspace_root: str = None) -> bool:
    """Runs a complete integrity verification audit on the repository's audit ledger."""
    root = workspace_root or os.getcwd()
    try:
        kernel = GovernanceKernel(root)
        return kernel.verify_integrity()
    except Exception:
        return False
