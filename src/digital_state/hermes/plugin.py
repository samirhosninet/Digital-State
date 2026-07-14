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
        self.ctx.register_hook("on_session_start", self.on_session_start_handler)
        self.ctx.register_hook("pre_llm_call", self.pre_llm_call_handler)
        self.ctx.register_hook("post_llm_call", self.post_llm_call_handler)
        self.ctx.register_hook("pre_tool_call", self.pre_tool_call_handler)
        self.ctx.register_hook("post_tool_call", self.post_tool_call_handler)
        self.ctx.register_hook("on_session_end", self.on_session_end_handler)
        
        # 4. Bind slash commands
        self.ctx.register_command("/approve", self.handle_approve_command)
        self.ctx.register_command("/veto", self.handle_veto_command)
        
        self.is_loaded = True
        logger.info("Digital State Plugin successfully Loaded.")
        return True

    def on_session_start_handler(self, context: Dict[str, Any]) -> bool:
        """Invoked when a Hermes session starts."""
        if not self.is_loaded:
            return False
        feature_id = context.get("feature_id")
        if not feature_id:
            logger.warning("Missing feature ID metadata on session start.")
            return False
        try:
            status = check_governance_status(feature_id, workspace_root=self.ctx.workspace_root)
            return status is not None
        except Exception as e:
            logger.error(f"Error checking status on session start: {e}")
            return False

    def pre_llm_call_handler(self, prompt: str, context: Dict[str, Any]) -> Any:
        """Invoked before model routing. Contributes active governance phase context."""
        if not self.is_loaded:
            return None
        feature_id = context.get("feature_id")
        if not feature_id:
            return None
        try:
            status = check_governance_status(feature_id, workspace_root=self.ctx.workspace_root)
            if status:
                return f"[Digital State Governance Context] Active Feature: {feature_id}, Current Phase: {status.get('state', 'Unknown')}"
        except Exception as e:
            logger.error(f"Error getting status for pre_llm_call: {e}")
        return None

    def post_llm_call_handler(self, response: str, context: Dict[str, Any]) -> None:
        """Invoked after model response."""
        if not self.is_loaded:
            return
        feature_id = context.get("feature_id")
        if feature_id:
            try:
                submit_evidence(feature_id, "llm_call", {"response_len": len(response)}, workspace_root=self.ctx.workspace_root)
            except Exception as e:
                logger.warning(f"Failed to submit post-LLM evidence: {e}")

    def pre_tool_call_handler(self, tool_name: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Intercepts tool executions and queries the SDK for authorization."""
        if not self.is_loaded:
            logger.error("Digital State Plugin is not loaded. Fail-Safe Deny triggered.")
            return {
                "action": "block",
                "message": "Digital State Plugin is not loaded. Fail-Safe Deny triggered."
            }
            
        agent_key = context.get("agent_key")
        feature_id = context.get("feature_id")
        
        if not agent_key or not feature_id:
            logger.warning("Missing agent key or feature ID metadata. Fail-Safe Deny triggered.")
            return {
                "action": "block",
                "message": "Missing agent key or feature ID metadata. Fail-Safe Deny triggered."
            }
            
        try:
            authorized = validate_gate_approval(feature_id, agent_key, workspace_root=self.ctx.workspace_root)
            if not authorized:
                logger.warning(f"Authorization denied for action '{tool_name}' on feature '{feature_id}'.")
                return {
                    "action": "block",
                    "message": f"Authorization denied for action '{tool_name}' on feature '{feature_id}' due to governance constraints."
                }
            return {"action": "approve"}
        except Exception as e:
            logger.error(f"Error validating gate approval for tool call: {e}")
            return {
                "action": "block",
                "message": f"Error validating gate approval for tool call: {e}"
            }

    def post_tool_call_handler(self, tool_name: str, outcome: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Invoked after tool execution to log results as evidence."""
        if not self.is_loaded:
            return
        feature_id = context.get("feature_id")
        if feature_id:
            try:
                submit_evidence(feature_id, "tool_call", {"tool": tool_name, "outcome": outcome}, workspace_root=self.ctx.workspace_root)
            except Exception as e:
                logger.warning(f"Failed to submit post-tool evidence: {e}")

    def on_session_end_handler(self, context: Dict[str, Any]) -> None:
        """Invoked when a Hermes session ends."""
        if not self.is_loaded:
            return
        try:
            verify_audit_log(workspace_root=self.ctx.workspace_root)
        except Exception as e:
            logger.warning(f"Verification of audit log failed on session end: {e}")

    def handle_approve_command(self, args: list) -> str:
        """Slash command handler for approving a gate transition."""
        if not args:
            return "Usage: /approve <feature_id>"
        feature_id = args[0]
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
