"""Canonical Installation Manifest Manager (ECR-BOOTSTRAP-ARCHITECTURE-002).

Manages %LOCALAPPDATA%\\digital-state\\installation.json tracking installer state,
runtime state, Hermes integration state, SpecKit state, profiles, and health.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class ManifestManager:
    """Manages reading, writing, and validating installation.json."""

    def __init__(self, target_dir: Optional[Path] = None):
        if target_dir:
            self.base_dir = Path(target_dir)
        else:
            if sys.platform == "win32":
                local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
                self.base_dir = Path(local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local")) / "digital-state"
            else:
                self.base_dir = Path(os.path.expanduser("~/.digital-state"))

        self.manifest_path = self.base_dir / "installation.json"
        self.tmp_manifest_path = self.base_dir / "installation.json.tmp"

    def ensure_directory(self) -> None:
        """Ensures storage directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load_manifest(self) -> Dict[str, Any]:
        """Loads manifest from disk or returns empty template if missing."""
        if not self.manifest_path.exists():
            return self.get_empty_template()
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else self.get_empty_template()
        except Exception:
            return self.get_empty_template()

    def save_manifest(self, data: Dict[str, Any]) -> bool:
        """Saves manifest to disk idempotently using atomic file swap."""
        try:
            self.ensure_directory()
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(self.tmp_manifest_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(self.tmp_manifest_path, self.manifest_path)
            return True
        except Exception:
            if self.tmp_manifest_path.exists():
                try:
                    self.tmp_manifest_path.unlink()
                except Exception:
                    pass
            return False

    def get_empty_template(self) -> Dict[str, Any]:
        """Returns baseline manifest template."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "$schema": "https://digitalstate.io/schemas/installation.v1.json",
            "installer_version": "1.16.0",
            "runtime_version": "1.16.0",
            "installation_state": "NOT_INSTALLED",
            "installed_at": now_iso,
            "updated_at": now_iso,
            "target_path": str(self.base_dir),
            "hermes_state": {
                "detected": False,
                "root": "",
                "python_path": "",
                "version": "Unknown"
            },
            "speckit_state": {
                "installed": False,
                "version": "Unknown"
            },
            "plugin_state": {
                "enabled": False,
                "entry_point": "digital_state = digital_state.hermes"
            },
            "profiles_state": {
                "prime": "MISSING",
                "builder": "MISSING",
                "auditor": "MISSING"
            },
            "health_status": "UNKNOWN"
        }
