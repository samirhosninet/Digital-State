"""Phase 1 Bootstrap Installer & Orchestrator (v1.14.0-bootstrap).

Provides idempotent bootstrap execution for initializing Digital State workspaces safely.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from digital_state.bootstrap.prereqs import PrerequisiteChecker


class BootstrapInstaller:
    """Idempotent installer orchestrator for Digital State workspace initialization."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(".")
        self.checker = PrerequisiteChecker()

    def run_bootstrap(self, dry_run: bool = False) -> Dict[str, Any]:
        """Executes idempotent workspace initialization and pre-flight checks."""
        prereqs = self.checker.run_all_checks()
        if not prereqs["is_healthy"]:
            return {
                "status": "FAILED",
                "message": "Prerequisite check failed.",
                "prerequisites": prereqs
            }

        specify_dir = self.workspace_root / ".specify"
        memory_dir = specify_dir / "memory"
        device_dir = specify_dir / "device"

        if dry_run:
            return {
                "status": "DRY_RUN_SUCCESS",
                "message": "Dry-run completed successfully. All prerequisites satisfied.",
                "workspace_root": str(self.workspace_root.resolve()),
                "prerequisites": prereqs,
                "planned_directories": [
                    str(specify_dir),
                    str(memory_dir),
                    str(device_dir)
                ]
            }

        # Idempotent directory creation
        specify_dir.mkdir(parents=True, exist_ok=True)
        memory_dir.mkdir(parents=True, exist_ok=True)
        device_dir.mkdir(parents=True, exist_ok=True)

        # Idempotent state.json initialization
        state_file = specify_dir / "state.json"
        if not state_file.exists() or state_file.stat().st_size == 0:
            state_file.write_text("{}", encoding="utf-8")

        # 1. Hermes Integration Auto-Configuration
        hermes_status = self.auto_configure_hermes()

        # 2. Automated Workspace Kernel Initialization
        workspace_status = self.auto_initialize_workspace()

        # 3. Device Identity Generation & 4-File Evidence Bundle Creation
        device_status = self.auto_provision_device_evidence(device_dir=device_dir)

        # 4. Idempotent integration.json initialization
        integration_file = specify_dir / "integration.json"
        integration_file.write_text(
            json.dumps({
                "integration": "hermes",
                "version": "1.14.0-bootstrap",
                "bootstrap": "zero_touch_complete",
                "hermes_status": hermes_status,
                "workspace_status": workspace_status,
                "device_status": device_status,
                "installed_at": "2026-07-20T04:35:00Z"
            }, indent=2),
            encoding="utf-8"
        )

        return {
            "status": "SUCCESS",
            "message": "Digital State zero-touch installation and bootstrap completed successfully.",
            "workspace_root": str(self.workspace_root.resolve()),
            "prerequisites": prereqs,
            "hermes_integration": hermes_status,
            "workspace_initialization": workspace_status,
            "device_provisioning": device_status,
            "directories_created": [
                str(specify_dir),
                str(memory_dir),
                str(device_dir)
            ]
        }

    def auto_configure_hermes(self) -> Dict[str, Any]:
        """Auto-detects Hermes root and registers digital_state plugin idempotently."""
        if sys.platform == "win32":
            local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
            hermes_root = os.environ.get("HERMES_HOME", "") or os.path.join(
                local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local"),
                "hermes"
            )
        else:
            hermes_root = os.environ.get("HERMES_HOME", "") or os.path.expanduser("~/.hermes")

        hermes_path = Path(hermes_root)
        config_path = hermes_path / "config.yaml"

        if not hermes_path.exists():
            return {
                "detected": False,
                "hermes_root": str(hermes_path),
                "message": "Hermes root directory not found; plugin registration deferred."
            }

        enabled_plugin = False
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                if "plugins" not in cfg or not isinstance(cfg["plugins"], dict):
                    cfg["plugins"] = {"enabled": []}
                if "enabled" not in cfg["plugins"] or not isinstance(cfg["plugins"]["enabled"], list):
                    cfg["plugins"]["enabled"] = []
                if "digital_state" not in cfg["plugins"]["enabled"]:
                    cfg["plugins"]["enabled"].append("digital_state")
                    with open(config_path, "w", encoding="utf-8") as f:
                        yaml.safe_dump(cfg, f, default_flow_style=False)
                enabled_plugin = True
            except Exception as e:
                return {
                    "detected": True,
                    "hermes_root": str(hermes_path),
                    "enabled": False,
                    "error": str(e)
                }

        # Seed profiles & profile manifests
        profiles = ["prime", "builder", "auditor"]
        seeded_manifests = []
        for p in profiles:
            p_dir = hermes_path / "profiles" / p
            p_dir.mkdir(parents=True, exist_ok=True)
            p_manifest = p_dir / "profile.yaml"
            if not p_manifest.exists():
                p_data = {
                    "name": f"Digital State {p.capitalize()} Profile",
                    "role": p,
                    "version": "1.14.0-bootstrap",
                    "permissions": ["evidence_read", "governance_audit"] if p == "auditor" else ["all"]
                }
                try:
                    import yaml
                    with open(p_manifest, "w", encoding="utf-8") as f:
                        yaml.safe_dump(p_data, f)
                    seeded_manifests.append(str(p_manifest))
                except Exception:
                    pass

        return {
            "detected": True,
            "hermes_root": str(hermes_path),
            "enabled": enabled_plugin,
            "profiles_seeded": profiles,
            "profile_manifests": seeded_manifests
        }


    def auto_initialize_workspace(self) -> Dict[str, Any]:
        """Initializes GovernanceKernel agent identities and initial state idempotently."""
        try:
            from digital_state.core.engine import GovernanceKernel
            kernel = GovernanceKernel(str(self.workspace_root), run_bootstrap=False)
            agents = kernel.registry.agents
            return {
                "initialized": True,
                "agent_count": len(agents),
                "agents": list(agents.keys())
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e)
            }


    def auto_provision_device_evidence(self, device_dir: Path) -> Dict[str, Any]:
        """Provisions ECDSA P-256 identity keypair and initial 4-file evidence bundle."""
        try:
            from digital_state.device.keystore import DeviceKeystore
            from digital_state.device.identity import DeviceIdentityManager
            from digital_state.device.evidence import EvidenceBundleManager
            from digital_state.governance.evidence.device_validator import DeviceEvidenceValidator

            keystore = DeviceKeystore(storage_dir=device_dir)
            identity_mgr = DeviceIdentityManager(keystore=keystore)
            identity_info = identity_mgr.get_identity_info()
            if not identity_info.get("has_key"):
                device_id, pub_pem, priv_pem = identity_mgr.generate_device_identity()
                identity_info = identity_mgr.get_identity_info()

            evidence_mgr = EvidenceBundleManager(device_dir=device_dir, identity_mgr=identity_mgr)
            bundle = evidence_mgr.generate_bundle()

            validator = DeviceEvidenceValidator(device_dir=device_dir)
            records = validator.validate_device_bundle(evidence_mgr=evidence_mgr)

            return {
                "provisioned": True,
                "device_id": identity_info.get("device_id", "uninitialized"),
                "bundle_files": list(bundle.keys()),
                "verified_records": len(records)
            }
        except Exception as e:
            return {
                "provisioned": False,
                "error": str(e)
            }


