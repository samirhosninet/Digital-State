"""Unit Tests for Phase 2 Device Evidence Validator (v1.13.0-platform).

Validates device evidence bundle validation, machine-readable JSON manifest generation,
and human-readable Markdown table generation for local host device.
"""

import json
import pytest
from pathlib import Path
from digital_state.governance.evidence import (
    EvidenceClassification,
    DeviceEvidenceValidator,
)
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.keystore import DeviceKeystore
from digital_state.device.evidence import EvidenceBundleManager


def test_device_evidence_validator_uninitialized(tmp_path):
    dev_dir = tmp_path / ".specify" / "device"
    validator = DeviceEvidenceValidator(device_dir=dev_dir)

    records = validator.validate_device_bundle()
    assert len(records) == 3
    # Uninitialized keystore and missing files should result in UNVERIFIED records
    assert any(r.classification == EvidenceClassification.UNVERIFIED for r in records)


def test_device_evidence_validator_initialized(tmp_path):
    dev_dir = tmp_path / ".specify" / "device"
    keystore = DeviceKeystore(storage_dir=dev_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)

    identity_mgr.generate_device_identity()

    evidence_mgr = EvidenceBundleManager(device_dir=dev_dir, identity_mgr=identity_mgr)
    evidence_mgr.generate_bundle()

    validator = DeviceEvidenceValidator(device_dir=dev_dir)
    records = validator.validate_device_bundle(evidence_mgr=evidence_mgr)

    assert len(records) == 3
    # All 3 device evidence records should be VERIFIED
    assert all(r.classification == EvidenceClassification.VERIFIED for r in records)

    # Validate JSON manifest generation
    manifest_json = validator.generate_device_evidence_manifest(evidence_mgr=evidence_mgr)
    manifest_data = json.loads(manifest_json)
    assert manifest_data["schema_version"] == "v1.0"
    assert manifest_data["total_records"] == 3

    # Validate Markdown table generation
    md_table = validator.generate_device_evidence_table(evidence_mgr=evidence_mgr)
    assert "| Statement | Evidence Type | Boundary | Source | Classification | Justification |" in md_table
    assert "Host Device ECDSA P-256 Keypair" in md_table
