"""Federated Evidence Manager (v1.15.0).

Aggregates multi-device 4-file evidence bundles into tenant-isolated federated manifests.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from digital_state.governance.evidence.device_validator import DeviceEvidenceValidator
from digital_state.governance.federation.attestation import RemoteAttestationVerifier


class FederatedEvidenceManager:
    """Manages multi-tenant evidence aggregation and cross-device attestation audit."""

    def __init__(self, tenant_id: str = "default_tenant"):
        self.tenant_id = tenant_id
        self.verifier = RemoteAttestationVerifier()

    def aggregate_device_bundles(
        self,
        device_bundles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregates multiple device evidence bundles into a federated tenant manifest.

        Args:
            device_bundles: List of device bundle dicts containing device_id, public_key_pem,
                            challenge_nonce, signature_hex, and evidence_records.

        Returns:
            Dict representing the Federated Evidence Manifest.
        """
        aggregated_records = []
        verified_devices = 0
        failed_devices = 0

        for dev in device_bundles:
            device_id = dev.get("device_id", "unknown_device")
            pub_key = dev.get("public_key_pem", "")
            nonce = dev.get("challenge_nonce", "")
            sig = dev.get("signature_hex", "")

            # Perform strict attestation check (Fail-Closed Default-Deny)
            if pub_key and nonce and sig:
                is_valid, msg = self.verifier.verify_device_attestation(pub_key, nonce, sig)
            else:
                is_valid = False
                msg = "Attestation omitted or missing cryptographic signature fields."

            if is_valid:
                verified_devices += 1
            else:
                failed_devices += 1

            records = dev.get("evidence_records", [])
            for r in records:
                r_copy = dict(r) if isinstance(r, dict) else r.to_dict()
                r_copy["tenant_id"] = self.tenant_id
                r_copy["device_id"] = device_id
                r_copy["attestation_valid"] = is_valid
                if not is_valid:
                    r_copy["classification"] = "UNVERIFIED"
                    r_copy["attestation_error"] = msg
                aggregated_records.append(r_copy)

        manifest = {
            "tenant_id": self.tenant_id,
            "manifest_type": "FEDERATED_EVIDENCE_MANIFEST",
            "schema_version": "v2.1-authenticated",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_devices": len(device_bundles),
            "verified_devices": verified_devices,
            "failed_devices": failed_devices,
            "total_records": len(aggregated_records),
            "records": aggregated_records
        }


        return manifest
