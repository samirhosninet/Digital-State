"""Unit tests for Phase 3 Device Enrollment Protocol (v1.11.0-device)."""

import json
import time
from pathlib import Path
from digital_state.device.keystore import DeviceKeystore
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.enrollment import EnrollmentProtocol


def test_1_valid_challenge_response_flow(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    protocol = EnrollmentProtocol(device_dir=device_dir, identity_mgr=identity_mgr)

    # 1. Create request
    req = protocol.create_enrollment_request()
    assert req["device_id"].startswith("dev_sha256_")

    # 2. Receive challenge
    challenge = EnrollmentProtocol.generate_challenge_nonce(ttl_seconds=300)
    assert len(challenge["challenge_nonce"]) == 64

    # 3. Sign challenge
    response = protocol.sign_challenge(challenge)
    assert response["device_id"] == req["device_id"]

    # 4. Verify & Enroll
    success, cert = protocol.verify_and_enroll(challenge, response)
    assert success is True
    assert cert["status"] == "ENROLLED"
    assert (device_dir / "device-certificate.json").exists()


def test_2_invalid_signature_rejection(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    protocol = EnrollmentProtocol(device_dir=device_dir, identity_mgr=identity_mgr)

    challenge = EnrollmentProtocol.generate_challenge_nonce(ttl_seconds=300)
    response = protocol.sign_challenge(challenge)

    # Tamper with signature hex
    response["signature"] = "00" * 32

    success, result = protocol.verify_and_enroll(challenge, response)
    assert success is False
    assert result["status"] == "REJECTED"
    assert "Invalid signature" in result["reason"]


def test_3_expired_challenge_rejection(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    protocol = EnrollmentProtocol(device_dir=device_dir, identity_mgr=identity_mgr)

    # Create expired challenge (-100s TTL)
    challenge = EnrollmentProtocol.generate_challenge_nonce(ttl_seconds=-100)
    response = protocol.sign_challenge(challenge)

    success, result = protocol.verify_and_enroll(challenge, response)
    assert success is False
    assert result["status"] == "REJECTED"
    assert "expired" in result["reason"]


def test_4_private_key_never_exported(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    protocol = EnrollmentProtocol(device_dir=device_dir, identity_mgr=identity_mgr)

    req = protocol.create_enrollment_request()
    challenge = EnrollmentProtocol.generate_challenge_nonce(ttl_seconds=300)
    response = protocol.sign_challenge(challenge)
    success, cert = protocol.verify_and_enroll(challenge, response)

    # Inspect all generated JSON artifacts
    for json_file in device_dir.glob("*.json"):
        content = json_file.read_text(encoding="utf-8")
        assert "PRIVATE KEY" not in content
        assert "PRIVATE_KEY" not in content
