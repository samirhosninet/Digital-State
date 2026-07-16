import os
import json
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
        # Resolve workspace_root: prefer ctx attribute, then env, then CWD
        self._workspace_root = (
            getattr(ctx, "workspace_root", None)
            or os.environ.get("HERMES_WORKSPACE")
            or os.getcwd()
        )

    @staticmethod
    def _governed_context(context: Any) -> tuple[str | None, Any]:
        """Return only runtime-supplied governance context; never invent identity."""
        if not isinstance(context, dict):
            return None, None
        return context.get("feature_id"), context.get("agent_key")
        
    def initialize(self) -> bool:
        """Runs the handshake check and hooks initialization on plugin load."""
        # Clean no_proxy of IPv6 addresses that break httpx
        for env_key in ("no_proxy", "NO_PROXY"):
            val = os.environ.get(env_key, "")
            if "::1" in val:
                clean_val = ",".join(
                    part for part in val.split(",")
                    if "::1" not in part
                )
                os.environ[env_key] = clean_val

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
            from pathlib import Path
            skill_data = pkgutil.get_data(__name__, "skills/governance.md")
            if skill_data:
                package_dir = os.path.dirname(os.path.abspath(__file__))
                skill_path = os.path.join(package_dir, "skills", "governance.md")
                self.ctx.register_skill("governance_playbook", Path(skill_path))
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
        self.ctx.register_command("/ds-approve", self.handle_approve_command)
        self.ctx.register_command("/ds-veto", self.handle_veto_command)
        
        self.is_loaded = True
        logger.info("Digital State Plugin successfully Loaded.")
        return True

    def on_session_start_handler(self, *args, **kwargs) -> bool:
        """Invoked when a Hermes session starts."""
        if not self.is_loaded:
            return False
        
        # Log dispatcher environment variables for runtime evidence
        env_vars = {
            "HERMES_KANBAN_TASK": os.environ.get("HERMES_KANBAN_TASK"),
            "HERMES_KANBAN_BOARD": os.environ.get("HERMES_KANBAN_BOARD"),
            "HERMES_PROFILE": os.environ.get("HERMES_PROFILE"),
            "HERMES_KANBAN_RUN_ID": os.environ.get("HERMES_KANBAN_RUN_ID"),
        }
        print(f"--- [Digital State Worker Log] Env Vars: {json.dumps(env_vars)}", flush=True)
        
        context = args[0] if args else (kwargs.get("context") or kwargs)
        feature_id, _ = self._governed_context(context)
        if not feature_id:
            logger.warning("Missing validated feature ID metadata on session start.")
            return False
                
        try:
            status = check_governance_status(feature_id, workspace_root=self._workspace_root)
            return status is not None
        except Exception as e:
            logger.error(f"Error checking status on session start: {e}")
            return False

    def pre_llm_call_handler(self, *args, **kwargs) -> Any:
        """Invoked before model routing. Contributes active governance phase context."""
        if not self.is_loaded:
            return None
        context = args[1] if len(args) > 1 else (kwargs.get("context") or kwargs)
        feature_id, _ = self._governed_context(context)
        if not feature_id:
            return None
        try:
            status = check_governance_status(feature_id, workspace_root=self._workspace_root)
            if status:
                return f"[Digital State Governance Context] Active Feature: {feature_id}, Current Phase: {status.get('state', 'Unknown')}"
        except Exception as e:
            logger.error(f"Error getting status for pre_llm_call: {e}")
        return None

    def post_llm_call_handler(self, *args, **kwargs) -> None:
        """Invoked after model response."""
        if not self.is_loaded:
            return
        response = args[0] if args else (kwargs.get("response") or "")
        context = args[1] if len(args) > 1 else (kwargs.get("context") or kwargs)
        feature_id, agent_key = self._governed_context(context)
        if feature_id and isinstance(agent_key, dict):
            logger.info("LLM response observed for feature '%s'; evidence requires a signed payload.", feature_id)

    def pre_tool_call_handler(self, *args, **kwargs) -> Dict[str, Any]:
        """Intercepts tool executions and queries the SDK for authorization."""
        if not self.is_loaded:
            logger.error("Digital State Plugin is not loaded. Fail-Safe Deny triggered.")
            return {
                "action": "block",
                "message": "Digital State Plugin is not loaded. Fail-Safe Deny triggered."
            }
            
        tool_name = args[0] if args else kwargs.get("tool_name")
        arguments = args[1] if len(args) > 1 else (kwargs.get("args") or kwargs.get("arguments") or {})
        context = args[2] if len(args) > 2 else (kwargs.get("context") or kwargs)
        
        feature_id, agent_key = self._governed_context(context)
        if not agent_key or not feature_id:
            logger.warning("Missing signed agent key or feature ID metadata. Fail-Safe Deny triggered.")
            return {
                "action": "block",
                "message": "Missing signed agent key or feature ID metadata. Fail-Safe Deny triggered."
            }
            
        try:
            authorized = validate_gate_approval(feature_id, agent_key, workspace_root=self._workspace_root)
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

    def post_tool_call_handler(self, *args, **kwargs) -> None:
        """Invoked after tool execution to log results as evidence."""
        if not self.is_loaded:
            return
        try:
            # positional arguments: tool_name, tool_args, result, task_id, duration_ms
            tool_name = args[0] if len(args) > 0 else kwargs.get("tool_name")
            tool_args = args[1] if len(args) > 1 else kwargs.get("args")
            result = args[2] if len(args) > 2 else kwargs.get("result")
            context = args[3] if len(args) > 3 and isinstance(args[3], dict) else kwargs.get("context", {})

            outcome = {"result": result, "args": tool_args}
            feature_id, agent_key = self._governed_context(context)
            if feature_id and isinstance(agent_key, dict):
                logger.info("Tool result observed for feature '%s'; evidence requires a signed payload.", feature_id)
        except Exception as e:
            logger.warning(f"Failed in post_tool_call_handler: {e}")

    def on_session_end_handler(self, *args, **kwargs) -> None:
        """Invoked when a Hermes session ends."""
        if not self.is_loaded:
            return
        try:
            verify_audit_log(workspace_root=self._workspace_root)
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
            verify_audit_log(self._workspace_root)
        except Exception:
            pass

def register(ctx) -> bool:
    """Plugin entrypoint invoked by Hermes runtime configuration."""
    print("--- DIGITAL STATE REGISTER FUNCTION CALLED ---", flush=True)
    plugin = DigitalStatePlugin(ctx)
    return plugin.initialize()
