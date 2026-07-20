"""Plugin & Profile Registrar Subsystem (ECR-BOOTSTRAP-ARCHITECTURE-002).

Performs atomic updates to config.yaml and seeds Hermes profile manifests.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List


class PluginRegistrar:
    """Manages atomic config.yaml updates and Hermes profile seeding."""

    def __init__(self, hermes_root: Path):
        self.hermes_root = hermes_root
        self.config_path = hermes_root / "config.yaml"
        self.tmp_config_path = hermes_root / "config.yaml.tmp"
        self.bak_config_path = hermes_root / "config.yaml.bak"

    def register_plugin(self) -> bool:
        """Enables digital_state in config.yaml using atomic file swap with backup."""
        if not self.hermes_root.exists():
            self.hermes_root.mkdir(parents=True, exist_ok=True)

        try:
            import yaml
            cfg = {}
            if self.config_path.exists():
                # Backup existing config before modification
                shutil.copy2(self.config_path, self.bak_config_path)
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}

            if "plugins" not in cfg or not isinstance(cfg["plugins"], dict):
                cfg["plugins"] = {"enabled": []}
            if "enabled" not in cfg["plugins"] or not isinstance(cfg["plugins"]["enabled"], list):
                cfg["plugins"]["enabled"] = []
            if "digital_state" not in cfg["plugins"]["enabled"]:
                cfg["plugins"]["enabled"].append("digital_state")

            with open(self.tmp_config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, default_flow_style=False)

            os.replace(self.tmp_config_path, self.config_path)
            return True
        except Exception:
            if self.tmp_config_path.exists():
                self.tmp_config_path.unlink(missing_ok=True)
            return False

    def seed_profiles(self) -> Dict[str, Any]:
        """Seeds prime, builder, and auditor profile manifests."""
        profiles = ["prime", "builder", "auditor"]
        seeded = []
        for p in profiles:
            p_dir = self.hermes_root / "profiles" / p
            p_dir.mkdir(parents=True, exist_ok=True)
            p_manifest = p_dir / "profile.yaml"
            tmp_manifest = p_dir / "profile.yaml.tmp"
            p_data = {
                "name": f"Digital State {p.capitalize()} Profile",
                "role": p,
                "version": "1.16.0",
                "permissions": ["evidence_read", "governance_audit"] if p == "auditor" else ["all"]
            }
            try:
                import yaml
                with open(tmp_manifest, "w", encoding="utf-8") as f:
                    yaml.safe_dump(p_data, f)
                os.replace(tmp_manifest, p_manifest)
                if p_manifest.exists():
                    seeded.append(p)
            except Exception:
                if tmp_manifest.exists():
                    tmp_manifest.unlink(missing_ok=True)

        return {
            "profiles_seeded": seeded,
            "all_seeded": len(seeded) == len(profiles)
        }
