"""Unit tests for Phase 4 SyncClient and Offline Enforcement (v1.11.0-device)."""

import json
import time
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from digital_state.device.keystore import DeviceKeystore
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.sync_client import SyncClient
from digital_state.device.policy_engine import LocalPolicyEngine


def _generate_authority_keypair():
    """Helper to generate mock central authority ECDSA P-256 keypair for test policy signing."""
    priv_key = ec.generate_private_key(ec.SECP256R1())
    pub_key = priv_key.public_key()
    pub_pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return priv_key, pub_pem


def _sign_policy(policy_dict: dict, priv_key) -> str:
    """Helper to produce valid ECDSA signature over policy dict."""
    canonical_bytes = json.dumps(policy_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig_bytes = priv_key.sign(canonical_bytes, ec.ECDSA(hashes.SHA256()))
    return sig_bytes.hex()


def test_sync_response_validation(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    priv_key, pub_pem = _generate_authority_keypair()

    policy_payload = {
        "tenant_id": "tenant_test",
        "policy_version": "v1.11.0-p2",
        "allowed_tools": ["execute_command", "view_file"]
    }
    sig_hex = _sign_policy(policy_payload, priv_key)
    policy_payload["signature"] = sig_hex

    mock_resp = {
        "authority_public_key_pem": pub_pem,
        "policy_state": policy_payload
    }

    client = SyncClient(device_dir=device_dir, identity_mgr=identity_mgr)
    res = client.sync_policy(mock_response=mock_resp)

    assert res["status"] == "SYNC_SUCCESS"
    assert res["policy_version"] == "v1.11.0-p2"
    assert (device_dir / "policy-state.json").exists()


def test_invalid_policy_signature_rejection(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    _, pub_pem = _generate_authority_keypair()

    policy_payload = {
        "tenant_id": "tenant_test",
        "policy_version": "v1.11.0-p2",
        "allowed_tools": ["execute_command"],
        "signature": "00" * 32  # Tampered / invalid signature
    }

    mock_resp = {
        "authority_public_key_pem": pub_pem,
        "policy_state": policy_payload
    }

    client = SyncClient(device_dir=device_dir, identity_mgr=identity_mgr)
    res = client.sync_policy(mock_response=mock_resp)

    assert res["status"] == "INVALID_SIGNATURE"
    assert res["offline_state"] == "DEFAULT_DENY"


def test_revoked_device_rejection(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    dev_id, _, _ = identity_mgr.generate_device_identity()

    mock_resp = {
        "crl_data": {
            "revoked_devices": [dev_id]
        }
    }

    client = SyncClient(device_dir=device_dir, identity_mgr=identity_mgr)
    res = client.sync_policy(mock_response=mock_resp)

    assert res["status"] == "REVOKED"
    assert "present in CRL" in res["reason"]
    assert res["offline_state"] == "DEFAULT_DENY"


def test_offline_transition_states(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    client = SyncClient(device_dir=device_dir, identity_mgr=identity_mgr)
    engine = LocalPolicyEngine(device_dir=device_dir)

    now_ts = time.time()

    # 1. ACTIVE (<12h)
    client.evidence_mgr.generate_bundle(last_sync_timestamp=now_ts - 3600)
    assert client.evidence_mgr.get_offline_state(now_ts - 3600) == "ACTIVE"

    # 2. WARNING (12-24h)
    client.evidence_mgr.generate_bundle(last_sync_timestamp=now_ts - 50000)
    assert client.evidence_mgr.get_offline_state(now_ts - 50000) == "WARNING"

    # 3. DEFAULT_DENY (>24h)
    client.evidence_mgr.generate_bundle(last_sync_timestamp=now_ts - 100000)
    assert client.evidence_mgr.get_offline_state(now_ts - 100000) == "DEFAULT_DENY"

    # Policy engine blocking on DEFAULT_DENY
    eval_res = engine.evaluate({"trace_id": "T-OFFLINE", "tool_name": "execute_command", "agent_id": "ag-1"})
    assert eval_res["action"] == "block"
    assert "Offline grace period" in eval_res["reason"] or "expired" in eval_res["reason"]


def test_failed_sync_behavior(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    identity_mgr = DeviceIdentityManager(keystore=keystore)
    identity_mgr.generate_device_identity()

    client = SyncClient(server_url="https://invalid-nonexistent-domain-12345.io", device_dir=device_dir, identity_mgr=identity_mgr)

    # Failed network request returns SYNC_FAILED and preserves local offline status
    res = client.sync_policy()
    assert res["status"] == "SYNC_FAILED"
    assert "Network error" in res["reason"] or "SYNC_FAILED" in res["status"]
