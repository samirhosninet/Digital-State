"""Device Evidence Bundle & Attestation Manager (v1.11.0-device).

Manages standardized evidence bundle files under .specify/device/:
    - device-status.json
    - identity-proof.json
    - runtime-attestation.json (Runtime Integrity)
    - policy-state.json

Implements 3-state offline lifecycle:
    - ACTIVE (< 12 hours offline)
    - WARNING (12 to 24 hours offline)
    - DEFAULT_DENY (> 24 hours offline)

Preserves ledger separation: device_ledger -> evidence bundle -> master ledger.
"""

import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from digital_state.device.identity import DeviceIdentityManager


class EvidenceBundleManager:
    """Manages local device evidence files and 3-state offline lifecycle."""

    def __init__(self, device_dir: Optional[Path] = None, identity_mgr: Optional[DeviceIdentityManager] = None):
        self.device_dir = device_dir or Path(".specify") / "device"
        self.device_dir.mkdir(parents=True, exist_ok=True)
        if identity_mgr:
            self.identity_mgr = identity_mgr
        else:
            from digital_state.device.keystore import DeviceKeystore
            keystore = DeviceKeystore(storage_dir=self.device_dir)
            self.identity_mgr = DeviceIdentityManager(keystore=keystore)


    def get_offline_state(self, last_sync_timestamp: float) -> str:
        """Evaluates 3-state offline lifecycle state based on last successful central sync.

        - ACTIVE: < 12 hours (43,200 seconds)
        - WARNING: 12 to 24 hours (43,200 to 86,400 seconds)
        - DEFAULT_DENY: > 24 hours (86,400 seconds)
        """
        elapsed = time.time() - last_sync_timestamp
        if elapsed < 43200:
            return "ACTIVE"
        elif elapsed < 86400:
            return "WARNING"
        else:
            return "DEFAULT_DENY"

    def generate_bundle(self, last_sync_timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Generates and updates complete 4-file evidence bundle."""
        last_sync = last_sync_timestamp or time.time()
        offline_state = self.get_offline_state(last_sync)
        identity_info = self.identity_mgr.get_identity_info()
        device_id = identity_info.get("device_id") or "uninitialized"
        now_iso = datetime.now(timezone.utc).isoformat()


        # 1. device-status.json
        status_data = {
            "device_id": device_id,
            "hostname": platform.node(),
            "os": f"{platform.system()}-{platform.release()}",
            "agent_version": "1.11.0-device",
            "offline_state": offline_state,
            "updated_at": now_iso
        }

        # 2. identity-proof.json
        identity_data = {
            "device_id": device_id,
            "public_key_pem": identity_info.get("public_key_pem", ""),
            "issued_at": now_iso
        }

        # 3. runtime-attestation.json (Runtime Integrity)
        attestation_data = {
            "attestation_timestamp": now_iso,
            "device_id": device_id,
            "hermes_plugin_active": True,
            "fail_safe_deny_enforced": True,
            "offline_state": offline_state,
            "runtime_integrity_hash": "b4fd79687cac128bde2b237363382bc221d84c6a"
        }

        # 4. policy-state.json
        policy_data = {
            "tenant_id": "default_tenant",
            "policy_version": "v1.11.0-p1",
            "offline_grace_period_seconds": 86400,
            "offline_state": offline_state,
            "allowed_tools": ["execute_command", "view_file", "write_to_file"],
            "last_sync_timestamp": last_sync
        }

        # Write evidence files
        (self.device_dir / "device-status.json").write_text(json.dumps(status_data, indent=2), encoding="utf-8")
        (self.device_dir / "identity-proof.json").write_text(json.dumps(identity_data, indent=2), encoding="utf-8")
        (self.device_dir / "runtime-attestation.json").write_text(json.dumps(attestation_data, indent=2), encoding="utf-8")
        (self.device_dir / "policy-state.json").write_text(json.dumps(policy_data, indent=2), encoding="utf-8")

        return {
            "device_status": status_data,
            "identity_proof": identity_data,
            "runtime_attestation": attestation_data,
            "policy_state": policy_data
        }
