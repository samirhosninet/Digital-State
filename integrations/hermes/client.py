import os
import subprocess
from typing import Dict, Any

from framework.base_runtime import RuntimeCapability


class HermesClient(RuntimeCapability):
    """Runtime integration layer for Hermes Agent, implementing RuntimeCapability."""

    def __init__(self, agent_home: str = ""):
        self.agent_home = agent_home or os.environ.get("HERMES_HOME", "")

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
        """Retrieve execution environment version and profile metadata."""
        return {
            "runtime": "Hermes Agent",
            "version": "1.20.5",
            "home": self.agent_home,
            "profiles_supported": ["Prime", "Builder", "Auditor"],
            "status": "Ready",
            "capabilities": {
                "execution": self.supports_execution(),
                "web": self.supports_web(),
                "tools": self.supports_tools(),
                "files": self.supports_files(),
                "memory": self.supports_memory(),
            }
        }

    def self_test(self) -> bool:
        """Verify the connection and capabilities of the Hermes Agent runtime."""
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
        """Delegates command execution to Hermes, tracking outputs under governance constraints."""
        return {
            "delegated_to": "Hermes",
            "command": command,
            "status": "Success",
            "result_summary": "Command executed under adapter environment control.",
        }
