"""Phase 2 Device Runtime Evidence Validator (v1.13.0-platform).

Provides additive validation for local host device evidence bundles (.specify/device/).
Evaluates 4-file evidence bundle integrity using EvidenceValidationEngine.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from digital_state.governance.evidence.models import (
    EvidenceRecord,
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
)
from digital_state.governance.evidence.engine import EvidenceValidationEngine
from digital_state.governance.evidence.report import EvidenceReportGenerator
from digital_state.device.evidence import EvidenceBundleManager


class DeviceEvidenceValidator:
    """Additive validator connecting local Device Runtime evidence with Evidence Governance engine."""

    def __init__(
        self,
        device_dir: Optional[Path] = None,
        validation_engine: Optional[EvidenceValidationEngine] = None,
    ):
        self.device_dir = device_dir or Path(".specify") / "device"
        self.engine = validation_engine or EvidenceValidationEngine()
        self.report_generator = EvidenceReportGenerator(validation_engine=self.engine)

    def validate_device_bundle(self, evidence_mgr: Optional[EvidenceBundleManager] = None) -> List[EvidenceRecord]:
        """Reads local device evidence files and converts them to validated EvidenceRecord instances."""
        mgr = evidence_mgr or EvidenceBundleManager(device_dir=self.device_dir)
        raw_bundle = mgr.generate_bundle()


        records = []

        # 1. Device Identity Proof
        has_identity = bool(raw_bundle.get("identity_proof", {}).get("public_key_pem"))
        records.append(
            self.engine.validate_record(
                EvidenceRecord(
                    statement="Host Device ECDSA P-256 Keypair in Secure Keystore",
                    evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
                    boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
                    source="src/digital_state/device/keystore.py",
                    classification=EvidenceClassification.VERIFIED if has_identity else EvidenceClassification.UNVERIFIED,
                    justification="Device identity keypair is initialized in OS keystore." if has_identity else "Uninitialized identity keypair.",
                    repo_path="src/digital_state/device/keystore.py",
                )
            )
        )

        # 2. Runtime Attestation & Deep Bundle Integrity
        bundle_files = ["device-status.json", "identity-proof.json", "runtime-attestation.json", "policy-state.json"]
        valid_bundle = True
        bundle_reason = "All 4 device evidence files exist with valid JSON structure."

        for f in bundle_files:
            file_path = self.device_dir / f
            if not file_path.exists() or file_path.stat().st_size == 0:
                valid_bundle = False
                bundle_reason = f"Missing or zero-byte evidence file: {f}"
                break
            try:
                content = json.loads(file_path.read_text(encoding="utf-8"))
                if not isinstance(content, dict) or not content:
                    valid_bundle = False
                    bundle_reason = f"Empty or non-dict JSON structure in: {f}"
                    break
            except Exception as e:
                valid_bundle = False
                bundle_reason = f"Malformed JSON in evidence file {f}: {e}"
                break

        cert_file = self.device_dir / "device-certificate.json"
        if cert_file.exists() and cert_file.stat().st_size > 0:
            try:
                cert_data = json.loads(cert_file.read_text(encoding="utf-8"))
                from digital_state.device.enrollment import EnrollmentProtocol
                if not EnrollmentProtocol.verify_certificate(cert_data):
                    valid_bundle = False
                    bundle_reason = "Invalid ECDSA CA certificate signature on device-certificate.json"
            except Exception:
                valid_bundle = False
                bundle_reason = "Corrupted device-certificate.json file"

        records.append(
            self.engine.validate_record(
                EvidenceRecord(
                    statement="Device Runtime 4-File Evidence Bundle Completeness & Integrity",
                    evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
                    boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
                    source="src/digital_state/device/evidence.py",
                    classification=EvidenceClassification.VERIFIED if valid_bundle else EvidenceClassification.UNVERIFIED,
                    justification=bundle_reason if valid_bundle else f"Integrity check failed: {bundle_reason}",
                    repo_path="src/digital_state/device/evidence.py",
                )
            )
        )



        # 3. Local Policy State
        offline_state = raw_bundle.get("policy_state", {}).get("offline_state", "UNKNOWN")
        is_active = offline_state in ("ACTIVE", "WARNING")
        records.append(
            self.engine.validate_record(
                EvidenceRecord(
                    statement=f"Device Policy Offline Enforcement State ({offline_state})",
                    evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
                    boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
                    source="src/digital_state/device/policy_engine.py",
                    classification=EvidenceClassification.VERIFIED if is_active else EvidenceClassification.UNVERIFIED,
                    justification=f"Device offline enforcement state is {offline_state}.",
                    repo_path="src/digital_state/device/policy_engine.py",
                )
            )
        )

        return records

    def generate_device_evidence_manifest(self, evidence_mgr: Optional[EvidenceBundleManager] = None) -> str:
        """Generates machine-readable JSON evidence manifest for local device runtime."""
        records = self.validate_device_bundle(evidence_mgr=evidence_mgr)
        return self.report_generator.render_json_manifest(records)

    def generate_device_evidence_table(self, evidence_mgr: Optional[EvidenceBundleManager] = None) -> str:
        """Generates human-readable Markdown evidence table for local device runtime."""
        records = self.validate_device_bundle(evidence_mgr=evidence_mgr)
        return self.report_generator.render_markdown_table(records)
