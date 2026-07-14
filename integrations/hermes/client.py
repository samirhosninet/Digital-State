"""Mock implementation of the Hermes Agent runtime adapter.

This module does NOT connect to a real Hermes instance. It provides a placeholder
implementation of the RuntimeCapability interface for development and testing.

Replace with a verified adapter when a real Hermes execution environment is available.
See integrations/hermes/README.md for the contract a real adapter must fulfill.
"""

import os
import subprocess
from typing import Dict, Any

from framework.base_runtime import RuntimeCapability


class HermesClient(RuntimeCapability):
    """Hermes Agent runtime adapter implementing RuntimeCapability.

    Supports running simulated plugin lifecycle loops for integration verification.
    """

    def __init__(self, agent_home: str = ""):
        self.agent_home = agent_home or os.environ.get("HERMES_HOME", "")
        self._is_mock = True

    def is_mock(self) -> bool:
        """Returns True if this is a mock adapter, False for a real/test integration."""
        return self._is_mock

    def set_mock_mode(self, is_mock: bool):
        """Toggle mock mode state for integration tests."""
        self._is_mock = is_mock

    def supports_execution(self) -> bool:
        return True

    def supports_web(self) -> bool:
        return False

    def supports_tools(self) -> bool:
        return True

    def supports_files(self) -> bool:
        return True

    def supports_memory(self) -> bool:
        return True

    def metadata(self) -> Dict[str, Any]:
        """Return hardcoded mock metadata. Does NOT query a real Hermes instance."""
        return {
            "runtime": "Hermes Agent",
            "version": "1.20.5",
            "home": self.agent_home,
            "profiles_supported": ["Prime", "Builder", "Auditor"],
            "status": "Ready",
            "mock": True,
            "capabilities": {
                "execution": self.supports_execution(),
                "web": self.supports_web(),
                "tools": self.supports_tools(),
                "files": self.supports_files(),
                "memory": self.supports_memory(),
            }
        }

    def self_test(self) -> bool:
        """Verify local tool availability (git). Does NOT test Hermes connectivity."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def execute_command_context(self, command: str) -> Dict[str, Any]:
        """Return a hardcoded mock response. Does NOT execute commands through Hermes."""
        return {
            "delegated_to": "Hermes",
            "command": command,
            "status": "Success",
            "mock": True,
            "result_summary": "Mock response — no actual execution occurred.",
        }

    def run_simulated_session(self, workspace_root: str, feature_id: str, agent_key: dict) -> Dict[str, Any]:
        """Runs the registered Digital State Plugin hooks in sequence to simulate a live Hermes session."""
        from digital_state.hermes.plugin import DigitalStatePlugin
        
        # Setup simulated context
        class RuntimeContext:
            def __init__(self, ws_root: str):
                self.workspace_root = ws_root
                self.skills = {}
                self.hooks = {}
                self.commands = {}
                
            def register_skill(self, name: str, path: str):
                self.skills[name] = path
                
            def register_hook(self, name: str, callback):
                self.hooks[name] = callback
                
            def register_command(self, name: str, callback):
                self.commands[name] = callback
                
        ctx = RuntimeContext(workspace_root)
        plugin = DigitalStatePlugin(ctx)
        
        if not plugin.initialize():
            return {"status": "HandshakeFailed"}
            
        session_ctx = {"feature_id": feature_id, "agent_key": agent_key}
        
        # 1. on_session_start
        start_ok = ctx.hooks["on_session_start"](session_ctx)
        if not start_ok:
            return {"status": "SessionStartDenied"}
            
        # 2. pre_llm_call
        llm_ok = ctx.hooks["pre_llm_call"]("Implement Feature X", session_ctx)
        if not llm_ok:
            return {"status": "LLMCallDenied"}
            
        # 3. post_llm_call
        ctx.hooks["post_llm_call"]("Proposed Plan", session_ctx)
        
        # 4. pre_tool_call
        tool_ok = ctx.hooks["pre_tool_call"]("write_file", {"file": "src/main.py"}, session_ctx)
        if not tool_ok:
            return {"status": "ToolCallDenied"}
            
        # 5. post_tool_call
        ctx.hooks["post_tool_call"]("write_file", {"success": True}, session_ctx)
        
        # 6. on_session_end
        ctx.hooks["on_session_end"](session_ctx)
        
        return {"status": "Success"}


