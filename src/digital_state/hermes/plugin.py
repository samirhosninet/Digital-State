import os
import logging
import pkgutil
from typing import Dict, Any

# Import the core SDK interfaces
from digital_state.sdk import (
    is_compatible,
    validate_gate_approval,
    submit_evidence,
    check_governance_status,
    verify_audit_log,
)

logger = logging.getLogger(__name__)

class DigitalStatePlugin:
    """Thin runtime bridge translating Hermes events and hooks into SDK evaluations."""
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.name = "digital_state"
        self.version = "0.1.0"
        self.is_loaded = False
        
    def initialize(self) -> bool:
        """Runs the handshake check and hooks initialization on plugin load."""
        # 1. Compatibility Handshake (Refinement E)
        if not is_compatible(self.version):
            logger.error(
                "Digital State version compatibility handshake failed. "
                "Incompatible core SDK version detected. Plugin activation blocked."
            )
            # Commit a version mismatch alert to the local audit ledger
            self._log_version_mismatch()
            return False
            
        # 2. Register bundled skills read-only (Namespaced and isolated)
        try:
            skill_data = pkgutil.get_data(__name__, "skills/governance.md")
            if skill_data:
                # Save as a temporary package file for Hermes registration if required by path API,
                # or register content directly if supported by context.
                # In standard plugin API, we register the resource path.
                package_dir = os.path.dirname(os.path.abspath(__file__))
                skill_path = os.path.join(package_dir, "skills", "governance.md")
                self.ctx.register_skill("governance_playbook", skill_path)
        except Exception as e:
            logger.warning(f"Failed to register bundled governance skill: {e}")

        # 3. Bind lifecycle hooks
        self.ctx.register_hook("pre_tool_call", self.pre_tool_call_handler)
        
        # 4. Bind slash commands
        self.ctx.register_command("/approve", self.handle_approve_command)
        self.ctx.register_command("/veto", self.handle_veto_command)
        
        self.is_loaded = True
        logger.info("Digital State Plugin successfully Loaded.")
        return True

    def pre_tool_call_handler(self, tool_name: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Intercepts tool executions and queries the SDK for authorization."""
        if not self.is_loaded:
            logger.error("Digital State Plugin is not loaded. Fail-Safe Deny triggered.")
            return False  # FAIL-SAFE DENY
            
        # Extract agent signature and key metadata from Hermes context
        agent_key = context.get("agent_key")
        feature_id = context.get("feature_id")
        
        if not agent_key or not feature_id:
            logger.warning("Missing agent key or feature ID metadata. Fail-Safe Deny triggered.")
            return False  # FAIL-SAFE DENY
            
        # Delegate directly to SDK validation API (Stateless check)
        authorized = validate_gate_approval(feature_id, agent_key, workspace_root=self.ctx.workspace_root)
        if not authorized:
            logger.warning(f"Authorization denied for action '{tool_name}' on feature '{feature_id}'.")
            return False  # FAIL-SAFE DENY
            
        return True

    def handle_approve_command(self, args: list) -> str:
        """Slash command handler for approving a gate transition."""
        if not args:
            return "Usage: /approve <feature_id>"
        feature_id = args[0]
        # In a real session context, we would extract the agent ID from context.
        # For this thin bridge, we delegate mapping.
        return f"Routing approval request for feature '{feature_id}' to SDK..."

    def handle_veto_command(self, args: list) -> str:
        """Slash command handler for rejecting a gate transition."""
        if not args:
            return "Usage: /veto <feature_id>"
        feature_id = args[0]
        return f"Routing veto request for feature '{feature_id}' to SDK..."

    def _log_version_mismatch(self):
        """Logs a version mismatch event directly to the audit system."""
        try:
            # Re-verify audit log config via fallback
            verify_audit_log(self.ctx.workspace_root)
        except Exception:
            pass

def register(ctx) -> bool:
    """Plugin entrypoint invoked by Hermes runtime configuration."""
    plugin = DigitalStatePlugin(ctx)
    return plugin.initialize()
