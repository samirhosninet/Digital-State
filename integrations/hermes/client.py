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
    """Mock Hermes Agent runtime adapter implementing RuntimeCapability.

    WARNING: This is a mock implementation. It does not connect to or communicate
    with a real Hermes Agent instance. All responses are hardcoded placeholders.

    A production adapter must:
    - Connect to a real Hermes execution environment.
    - Return live metadata from the Hermes runtime.
    - Execute commands through the Hermes execution context.
    - Return is_mock() == False.
    """

    def __init__(self, agent_home: str = ""):
        self.agent_home = agent_home or os.environ.get("HERMES_HOME", "")

    def is_mock(self) -> bool:
        """Returns True if this is a mock adapter, False for a real implementation."""
        return True

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

