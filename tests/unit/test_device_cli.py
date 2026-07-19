"""Unit tests for Phase 1 Device CLI & Identity Foundation (v1.11.0-device)."""

import json
import time
from pathlib import Path
from digital_state.device.keystore import DeviceKeystore
from digital_state.device.identity import DeviceIdentityManager
from digital_state.device.evidence import EvidenceBundleManager
from digital_state.device.cli import main as device_cli_main


def test_device_keystore_and_identity_generation(tmp_path):
    keystore = DeviceKeystore(storage_dir=tmp_path)
    mgr = DeviceIdentityManager(keystore=keystore)

    assert keystore.has_stored_key() is False

    device_id, pub_pem, priv_pem = mgr.generate_device_identity()

    assert device_id.startswith("dev_sha256_")
    assert keystore.has_stored_key() is True
    assert keystore.retrieve_private_key() == priv_pem

    # Test signature
    sig = mgr.sign_payload(b"test_payload")
    assert len(sig) > 0

    info = mgr.get_identity_info()
    assert info["status"] == "ACTIVE"
    assert info["device_id"] == device_id


def test_device_evidence_bundle_and_offline_lifecycle(tmp_path):
    device_dir = tmp_path / "device"
    keystore = DeviceKeystore(storage_dir=device_dir)
    mgr = DeviceIdentityManager(keystore=keystore)
    mgr.generate_device_identity()

    evidence_mgr = EvidenceBundleManager(device_dir=device_dir, identity_mgr=mgr)

    # 1. Active state (< 12 hours)
    now_ts = time.time()
    assert evidence_mgr.get_offline_state(now_ts - 3600) == "ACTIVE"

    # 2. Warning state (12 to 24 hours)
    assert evidence_mgr.get_offline_state(now_ts - 50000) == "WARNING"

    # 3. Default Deny state (> 24 hours)
    assert evidence_mgr.get_offline_state(now_ts - 100000) == "DEFAULT_DENY"

    bundle = evidence_mgr.generate_bundle(last_sync_timestamp=now_ts)
    assert (device_dir / "device-status.json").exists()
    assert (device_dir / "identity-proof.json").exists()
    assert (device_dir / "runtime-attestation.json").exists()
    assert (device_dir / "policy-state.json").exists()

    assert bundle["device_status"]["offline_state"] == "ACTIVE"
    assert bundle["runtime_attestation"]["fail_safe_deny_enforced"] is True


def test_device_cli_init_verify_doctor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # 1. doctor before init -> WARN/FAIL
    ret_doc0 = device_cli_main(["doctor"])
    assert ret_doc0 in (0, 1)

    # 2. init
    ret_init = device_cli_main(["init"])
    assert ret_init == 0

    # 3. verify
    ret_ver = device_cli_main(["verify"])
    assert ret_ver == 0

    # 4. doctor after init -> PASS
    ret_doc1 = device_cli_main(["doctor"])
    assert ret_doc1 == 0

    # 5. verify-ledger
    ret_led = device_cli_main(["verify-ledger"])
    assert ret_led == 0
