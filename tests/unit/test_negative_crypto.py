"""Negative Cryptographic & Security Edge Case Test Suite (TASK-013-F1).

Verifies Fail-Closed security behavior across cryptographic operations:
- Tampered signature rejection
- Expired nonce challenge rejection
- Invalid certificate signature rejection
- Corrupted AES-256-GCM keystore ciphertext decryption failure
- Missing federation attestation signature rejection
"""

import json
import time
import pytest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes

from digital_state.device.keystore import DeviceKeystore
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.enrollment import EnrollmentProtocol
from digital_state.governance.federation.manager import FederatedEvidenceManager
from digital_state.core.verifier import CryptoVerifier
from digital_state.core.exceptions import EvidenceError


def test_negative_tampered_payload_signature(tmp_path):
    """Tampering with signed payload content must cause verification failure."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    payload = {"action": "approve", "amount": 100}
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
    sig_hex = priv.sign(serialized, ec.ECDSA(hashes.SHA256())).hex()

    key_meta = {
        "key_id": "test-key",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pub_pem
    }

    # Tamper payload
    tampered_payload = {"action": "approve", "amount": 999999}
    with pytest.raises(EvidenceError):
        CryptoVerifier.verify(key_meta, tampered_payload, sig_hex)


def test_negative_expired_enrollment_nonce(tmp_path):
    """Expired challenge nonces must be rejected during enrollment."""
    device_dir = tmp_path / ".specify" / "device"
    enrollment = EnrollmentProtocol(device_dir=device_dir)
    enrollment.create_enrollment_request()

    # Challenge issued in the past (expired 60s ago)
    past_ts = time.time() - 600
    challenge = {
        "challenge_nonce": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "issued_at": past_ts,
        "expires_at": past_ts + 300
    }
    response = enrollment.sign_challenge(challenge)

    success, res = enrollment.verify_and_enroll(challenge, response)
    assert success is False
    assert res["status"] == "REJECTED"
    assert "expired" in res["reason"].lower()


def test_negative_invalid_ca_certificate_signature(tmp_path):
    """Tampered or invalid certificate signatures must fail verify_certificate()."""
    device_dir = tmp_path / ".specify" / "device"
    enrollment = EnrollmentProtocol(device_dir=device_dir)
    enrollment.create_enrollment_request()
    challenge = enrollment.generate_challenge_nonce()
    response = enrollment.sign_challenge(challenge)


    success, cert_data = enrollment.verify_and_enroll(challenge, response)
    assert success is True
    assert enrollment.verify_certificate(cert_data) is True

    # Tamper certificate signature
    tampered_cert = dict(cert_data)
    tampered_cert["certificate_signature"] = "a" * 128
    assert enrollment.verify_certificate(tampered_cert) is False


def test_negative_corrupted_keystore_ciphertext(tmp_path):
    """Corrupted AES-256-GCM ciphertext payload must return None on retrieval."""
    device_dir = tmp_path / ".specify" / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    keystore.store_private_key(b"test_private_key")

    enc_file = device_dir / "keystore.enc"
    assert enc_file.exists()

    # Corrupt ciphertext file
    enc_file.write_bytes(b"AESGCM:0000:0000:invalid_base64_data")
    assert keystore.retrieve_private_key() is None


def test_negative_federation_omitted_attestation_rejection():
    """Federated evidence manager must mark bundles with omitted signatures as UNVERIFIED."""
    fed_mgr = FederatedEvidenceManager(tenant_id="test_tenant")
    unattested_bundle = [{
        "device_id": "malicious_node",
        "evidence_records": [{"statement": "unattested_record", "classification": "VERIFIED"}]
    }]

    manifest = fed_mgr.aggregate_device_bundles(unattested_bundle)
    assert manifest["verified_devices"] == 0
    assert manifest["failed_devices"] == 1
    assert manifest["records"][0]["attestation_valid"] is False
    assert manifest["records"][0]["classification"] == "UNVERIFIED"
