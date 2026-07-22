"""SpecKit Provisioner Subsystem (ECR-BOOTSTRAP-ARCHITECTURE-002).

Provisions SpecKit CLI management suite inside Hermes runtime.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any


class SpeckitProvisioner:
    """Manages SpecKit CLI integration."""

    def __init__(self, hermes_python: Path):
        self.hermes_python = hermes_python

    def provision_speckit(self) -> Dict[str, Any]:
        """Verifies or installs SpecKit CLI suite.

        SpecKit is an optional, non-blocking component. Report its real status
        rather than always claiming success, so the manifest reflects reality.
        """
        try:
            res = subprocess.run([str(self.hermes_python), "-c", "import speckit; import importlib.metadata as m; print(m.version('speckit'))"], capture_output=True, text=True)
            installed = res.returncode == 0
            version = res.stdout.strip() if installed else "0.0.0"
        except Exception:
            installed = False
            version = "0.0.0"

        return {
            "installed": installed,
            "version": version,
            "blocking": False
        }
