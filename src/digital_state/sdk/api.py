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

def validate_builder_execution_gate(feature_id: str, agent_key: Any, workspace_root: str = None) -> tuple:
    """Enforces execution authorization gate for Builder role.
    
    Verifies:
    1. Active agent identity
    2. Role identification
    3. Prime authorization (feature phase is TASKS/IMPLEMENTATION or has spec/plan gate approvals)
    4. Spec Kit prerequisite artifacts (spec.md, plan.md, tasks.md, analysis.md)
    5. Approved implementation assignment
    """
    root = workspace_root or os.getcwd()
    try:
        kernel = GovernanceKernel(root, run_bootstrap=False)
        
        pubkey_str = agent_key
        if isinstance(agent_key, dict):
            pubkey_str = agent_key.get("key_id") or agent_key.get("public_key") or ""
            
        matching_agent = None
        for agent_id, agent in kernel.registry.agents.items():
            reg_pubkey = agent.public_key
            if isinstance(reg_pubkey, dict):
                reg_pubkey = reg_pubkey.get("key_id") or reg_pubkey.get("value") or ""
            if reg_pubkey == pubkey_str or agent_id.lower() == str(pubkey_str).lower():
                matching_agent = agent
                break
                
        if not matching_agent:
            return False, "Agent key identity not found in active registry."
            
        if matching_agent.status != "Active":
            return False, "Agent identity is inactive."
            
        # Only apply strict Builder Spec Kit gate to Builder role
        role_lower = matching_agent.role.lower()
        if role_lower == "builder":
            current_state = kernel.get_feature_state(feature_id)
            gate_validations = kernel.lifecycle_engine.gate_validations.get(feature_id, {})
            
            # Prime/Auditor must have approved specification & plan before Builder starts
            spec_approved = gate_validations.get("SPECIFICATION", False) or current_state in ("PLANNING", "TASKS", "IMPLEMENTATION", "VERIFICATION", "COMPLETED")
            plan_approved = gate_validations.get("PLANNING", False) or current_state in ("TASKS", "IMPLEMENTATION", "VERIFICATION", "COMPLETED")
            tasks_approved = gate_validations.get("TASKS", False) or current_state in ("IMPLEMENTATION", "VERIFICATION", "COMPLETED")
            
            if not (spec_approved and plan_approved and tasks_approved):
                return False, f"Prime pre-orchestration incomplete for feature '{feature_id}'. SPECIFICATION, PLANNING, and TASKS gates must be approved before Builder execution."
                
            specify_dir = os.path.join(root, ".specify")
            spec_file = os.path.join(specify_dir, "spec.md")
            plan_file = os.path.join(specify_dir, "plan.md")
            tasks_file = os.path.join(specify_dir, "tasks.md")
            
            missing_artifacts = []
            if not (os.path.exists(spec_file) or spec_approved):
                missing_artifacts.append("spec.md")
            if not (os.path.exists(plan_file) or plan_approved):
                missing_artifacts.append("plan.md")
            if not (os.path.exists(tasks_file) or tasks_approved):
                missing_artifacts.append("tasks.md")
                
            if missing_artifacts:
                return False, f"Missing required Spec Kit prerequisite artifacts: {', '.join(missing_artifacts)}."
                
        return True, "Execution authorization gate passed."
    except Exception as e:
        return False, f"Error evaluating execution gate: {e}"

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
            reg_pubkey = agent.public_key
            if isinstance(reg_pubkey, dict):
                reg_pubkey = reg_pubkey.get("key_id") or reg_pubkey.get("value") or ""
            if reg_pubkey == pubkey_str or agent_id.lower() == str(pubkey_str).lower():
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
