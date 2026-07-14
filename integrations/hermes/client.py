"""Live implementation of the Hermes Agent runtime adapter.

Connects directly to the native Hermes runtime.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any

from framework.base_runtime import RuntimeCapability


class HermesClient(RuntimeCapability):
    """Hermes Agent runtime adapter implementing RuntimeCapability.

    Coordinates execution and verification directly via the real Hermes Agent CLI.
    """

    def __init__(self, agent_home: str = ""):
        if sys.platform == "win32":
            local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
            self.agent_home = agent_home or os.environ.get("HERMES_HOME", "") or os.path.join(
                local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local"),
                "hermes"
            )
        else:
            self.agent_home = agent_home or os.environ.get("HERMES_HOME", "") or os.path.expanduser("~/.hermes")
        
        # Default to False (LIVE mode) when Hermes is detected on the system, otherwise fallback to True for tests.
        self._is_mock = not self.self_test()

    def is_mock(self) -> bool:
        """Returns True if this is a mock adapter, False for a real/test integration."""
        return self._is_mock

    def set_mock_mode(self, is_mock: bool):
        """Toggle mock mode state for integration tests."""
        self._is_mock = is_mock

    def supports_execution(self) -> bool:
        return True

    def supports_web(self) -> bool:
        return True

    def supports_tools(self) -> bool:
        return True

    def supports_files(self) -> bool:
        return True

    def supports_memory(self) -> bool:
        return True

    def _get_hermes_cmd(self) -> str | None:
        import shutil
        hermes_cmd = shutil.which("hermes")
        if not hermes_cmd:
            if sys.platform == "win32":
                h_path = os.path.join(self.agent_home, "hermes-agent", "venv", "Scripts", "hermes.exe")
                if os.path.exists(h_path):
                    hermes_cmd = h_path
            else:
                h_path = os.path.join(self.agent_home, "hermes-agent", "venv", "bin", "hermes")
                if os.path.exists(h_path):
                    hermes_cmd = h_path
        return hermes_cmd

    def metadata(self) -> Dict[str, Any]:
        """Return real Hermes Agent metadata."""
        hermes_cmd = self._get_hermes_cmd()
        version = "Unknown"
        if hermes_cmd:
            try:
                res = subprocess.run(
                    [hermes_cmd, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                if res.returncode == 0:
                    version = res.stdout.strip()
            except Exception:
                pass

        # Detect provisioned profiles
        profiles = ["default"]
        profiles_dir = os.path.join(self.agent_home, "profiles")
        if os.path.exists(profiles_dir):
            for name in os.listdir(profiles_dir):
                if os.path.isdir(os.path.join(profiles_dir, name)):
                    profiles.append(name)

        return {
            "runtime": "Hermes Agent",
            "version": version,
            "home": self.agent_home,
            "profiles_supported": profiles,
            "status": "Ready" if hermes_cmd else "Offline",
            "mock": self._is_mock,
            "capabilities": {
                "execution": self.supports_execution(),
                "web": self.supports_web(),
                "tools": self.supports_tools(),
                "files": self.supports_files(),
                "memory": self.supports_memory(),
            }
        }

    def self_test(self) -> bool:
        """Verify Hermes binary availability."""
        hermes_cmd = self._get_hermes_cmd()
        if not hermes_cmd:
            return False
        try:
            result = subprocess.run(
                [hermes_cmd, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute_command_context(self, command: str) -> Dict[str, Any]:
        """Execute commands through the real Hermes Agent runtime (using Builder profile)."""
        hermes_cmd = self._get_hermes_cmd()
        if not hermes_cmd:
            return {
                "status": "Error",
                "error": "Hermes executable not found"
            }
        try:
            res = subprocess.run(
                [hermes_cmd, "-p", "builder", "chat", "-q", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return {
                "status": "Success" if res.returncode == 0 else "Error",
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode
            }
        except Exception as e:
            return {
                "status": "Error",
                "error": str(e)
            }

    def run_simulated_session(self, workspace_root: str, feature_id: str, agent_key: dict) -> Dict[str, Any]:
        """Runs the registered Digital State Plugin hooks in sequence to simulate a live Hermes session."""
        from digital_state.hermes.plugin import DigitalStatePlugin
        
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
        from digital_state.sdk import validate_gate_approval
        try:
            if not validate_gate_approval(feature_id, agent_key, workspace_root=workspace_root):
                return {"status": "LLMCallDenied"}
        except Exception:
            return {"status": "LLMCallDenied"}
        
        ctx.hooks["pre_llm_call"]("Implement Feature X", session_ctx)
            
        # 3. post_llm_call
        ctx.hooks["post_llm_call"]("Proposed Plan", session_ctx)
        
        # 4. pre_tool_call
        tool_result = ctx.hooks["pre_tool_call"]("write_file", {"file": "src/main.py"}, session_ctx)
        if isinstance(tool_result, dict) and tool_result.get("action") == "block":
            return {"status": "ToolCallDenied"}
            
        # 5. post_tool_call
        ctx.hooks["post_tool_call"]("write_file", {"success": True}, session_ctx)
        
        # 6. on_session_end
        ctx.hooks["on_session_end"](session_ctx)
        
        return {"status": "Success"}
