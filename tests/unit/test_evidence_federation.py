"""Unit Tests for Evidence Federation Subsystem (v1.15.0).

Validates multi-tenant evidence aggregation, attestation signature checks, and CLI federation options.
"""

import pytest
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.keystore import DeviceKeystore
from digital_state.governance.federation.attestation import RemoteAttestationVerifier
from digital_state.governance.federation.manager import FederatedEvidenceManager


def test_remote_attestation_verifier(tmp_path):
    keystore = DeviceKeystore(storage_dir=tmp_path)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    device_id, pub_pem, priv_pem = identity_mgr.generate_device_identity()
    pub_pem_str = pub_pem.decode("utf-8")

    nonce = "test_challenge_nonce_12345"
    sig_bytes = identity_mgr.sign_payload(nonce.encode("utf-8"))
    sig_hex = sig_bytes.hex()

    verifier = RemoteAttestationVerifier()
    is_valid, msg = verifier.verify_device_attestation(pub_pem_str, nonce, sig_hex)

    assert is_valid is True
    assert "valid" in msg.lower()

    # Invalid signature check
    invalid_sig = "00" * len(sig_bytes)
    is_valid_bad, msg_bad = verifier.verify_device_attestation(pub_pem_str, nonce, invalid_sig)
    assert is_valid_bad is False


def test_federated_evidence_manager(tmp_path):
    keystore = DeviceKeystore(storage_dir=tmp_path)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    device_id, pub_pem, priv_pem = identity_mgr.generate_device_identity()
    pub_pem_str = pub_pem.decode("utf-8")

    nonce = "nonce_abc_999"
    sig_bytes = identity_mgr.sign_payload(nonce.encode("utf-8"))
    sig_hex = sig_bytes.hex()

    fed_mgr = FederatedEvidenceManager(tenant_id="tenant_alpha")
    manifest = fed_mgr.aggregate_device_bundles([{
        "device_id": device_id,
        "public_key_pem": pub_pem_str,
        "challenge_nonce": nonce,
        "signature_hex": sig_hex,
        "evidence_records": [{
            "record_id": "rec_001",
            "statement": "Device attestation test statement",
            "classification": "VERIFIED",
            "evidence_type": "Repository Implementation Evidence",
            "boundary": "Digital State Repository",
            "source_reference": "test_evidence_federation.py",
            "justification": "Valid attestation signature"
        }]
    }])

    assert manifest["tenant_id"] == "tenant_alpha"
    assert manifest["verified_devices"] == 1
    assert manifest["failed_devices"] == 0
    assert len(manifest["records"]) == 1
    assert manifest["records"][0]["attestation_valid"] is True
