"""Phase 1 Bootstrap Prerequisite Checker (v1.14.0-bootstrap).

Detects system environment prerequisites safely (Python 3.11+, pip, virtualenv).
"""

import sys
import shutil
import platform
from typing import Dict, Any


class PrerequisiteChecker:
    """Detects prerequisite environment state and dependencies."""

    @staticmethod
    def check_python_version() -> Dict[str, Any]:
        """Verifies Python version is 3.11 or higher."""
        major, minor, micro = sys.version_info[:3]
        is_supported = (major == 3 and minor >= 11) or major > 3
        return {
            "component": "python",
            "version": f"{major}.{minor}.{micro}",
            "is_supported": is_supported,
            "message": f"Python {major}.{minor}.{micro} detected." if is_supported else "Python 3.11+ required."
        }

    @staticmethod
    def check_system_platform() -> Dict[str, Any]:
        """Detects host operating system and architecture."""
        return {
            "component": "platform",
            "os": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "architecture": platform.machine()
        }

    @staticmethod
    def check_tools() -> Dict[str, Any]:
        """Checks availability of system tools (git, pip)."""
        git_path = shutil.which("git")
        pip_path = shutil.which("pip") or shutil.which("pip3")
        return {
            "has_git": bool(git_path),
            "git_path": git_path or "",
            "has_pip": bool(pip_path),
            "pip_path": pip_path or ""
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """Runs complete prerequisite verification suite."""
        py_check = self.check_python_version()
        plat_check = self.check_system_platform()
        tools_check = self.check_tools()

        is_healthy = py_check["is_supported"] and tools_check["has_pip"]

        return {
            "is_healthy": is_healthy,
            "python": py_check,
            "platform": plat_check,
            "tools": tools_check
        }
