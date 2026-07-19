"""Unit tests for Device Ledger SHA-256 hash chaining (v1.11.0-device)."""

import json
from pathlib import Path
from digital_state.device.device_ledger import DeviceLedger


def test_device_ledger_append_and_verify(tmp_path):
    ledger_file = tmp_path / "device_ledger.jsonl"
    ledger = DeviceLedger(ledger_path=ledger_file)

    # Initial empty verification
    res0 = ledger.verify_chain()
    assert res0["status"] == "VALID"
    assert res0["total_entries"] == 0

    # Append entry 1
    e1 = ledger.append("TRACE-001", {"action": "approve"})
    assert e1["previous_hash"] == "0" * 64
    assert len(e1["current_hash"]) == 64

    # Append entry 2
    e2 = ledger.append("TRACE-002", {"action": "block", "reason": "test"})
    assert e2["previous_hash"] == e1["current_hash"]

    # Verify chain intact
    res1 = ledger.verify_chain()
    assert res1["status"] == "VALID"
    assert res1["total_entries"] == 2
    assert res1["chain_intact"] is True


def test_device_ledger_tamper_detection(tmp_path):
    ledger_file = tmp_path / "device_ledger.jsonl"
    ledger = DeviceLedger(ledger_path=ledger_file)

    ledger.append("TRACE-001", {"action": "approve"})
    ledger.append("TRACE-002", {"action": "approve"})

    # Tamper with line 1
    lines = ledger_file.read_text(encoding="utf-8").splitlines()
    data0 = json.loads(lines[0])
    data0["decision"]["action"] = "tampered_action"
    lines[0] = json.dumps(data0)
    ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    res_tamper = ledger.verify_chain()
    assert res_tamper["status"] == "TAMPERED"
    assert res_tamper["corrupted_line"] == 1
    assert res_tamper["chain_intact"] is False
