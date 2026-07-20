"""Dependency Manager Subsystem (ECR-BOOTSTRAP-ARCHITECTURE-002).

Inspects host environment for Python 3.10+, pip, and virtualenv capabilities.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class DependencyManager:
    """Manages Python 3.10+ and pip runtime dependency detection."""

    def __init__(self):
        self.python_cmd: Optional[str] = self._locate_python()

    def _locate_python(self) -> Optional[str]:
        py = shutil.which("python") or shutil.which("python3")
        if py:
            return py
        if sys.executable and Path(sys.executable).exists():
            return sys.executable
        return None

    def verify_dependencies(self) -> Dict[str, Any]:
        """Verifies Python version and pip availability."""
        if not self.python_cmd:
            return {
                "python_installed": False,
                "supported": False,
                "version": "Missing",
                "pip_available": False
            }

        try:
            ver_res = subprocess.run([self.python_cmd, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True)
            ver_str = ver_res.stdout.strip()
            major, minor = map(int, ver_str.split("."))
            supported = (major == 3 and minor >= 10) or major > 3
        except Exception:
            supported = False
            ver_str = "Unknown"

        try:
            pip_res = subprocess.run([self.python_cmd, "-m", "pip", "--version"], capture_output=True, text=True)
            pip_ok = pip_res.returncode == 0
        except Exception:
            pip_ok = False

        return {
            "python_installed": True,
            "python_path": self.python_cmd,
            "supported": supported,
            "version": ver_str,
            "pip_available": pip_ok
        }
