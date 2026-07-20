"""Hermes Provisioner Subsystem (ECR-BOOTSTRAP-ARCHITECTURE-002).

Detects or provisions Hermes Agent runtime under %LOCALAPPDATA%\\hermes\\.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class HermesProvisioner:
    """Manages Hermes Agent runtime path resolution and venv python detection."""

    def __init__(self, override_root: Optional[Path] = None):
        if override_root:
            self.hermes_root = Path(override_root)
        else:
            if sys.platform == "win32":
                local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
                self.hermes_root = Path(os.environ.get("HERMES_HOME", "") or os.path.join(
                    local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local"),
                    "hermes"
                ))
            else:
                self.hermes_root = Path(os.environ.get("HERMES_HOME", "") or os.path.expanduser("~/.hermes"))

    def resolve_hermes_python(self) -> Path:
        """Resolves Hermes Python executable path."""
        if sys.platform == "win32":
            p = self.hermes_root / "hermes-agent" / "venv" / "Scripts" / "python.exe"
        else:
            p = self.hermes_root / "hermes-agent" / "venv" / "bin" / "python"

        if p.exists():
            return p

        # Check PATH fallback
        h_cmd = shutil.which("hermes")
        if h_cmd:
            cmd_dir = Path(h_cmd).parent
            p_cmd = cmd_dir / ("python.exe" if sys.platform == "win32" else "python")
            if p_cmd.exists():
                return p_cmd

        return Path(sys.executable)

    def provision_hermes_runtime(self) -> Dict[str, Any]:
        """Provisions or verifies Hermes runtime directory structure."""
        if not self.hermes_root.exists():
            self.hermes_root.mkdir(parents=True, exist_ok=True)

        h_python = self.resolve_hermes_python()

        return {
            "detected": self.hermes_root.exists(),
            "hermes_root": str(self.hermes_root),
            "hermes_python": str(h_python),
            "python_exists": h_python.exists()
        }
