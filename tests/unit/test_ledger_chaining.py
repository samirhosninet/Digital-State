"""Unit tests for cryptographic audit log signature chaining (012-audit-log-signature-chaining)."""

import json
import importlib.util
from pathlib import Path

# Load Ledger dynamically due to hyphen in self-governance path
ledger_py = Path(__file__).resolve().parent.parent.parent / "governance" / "self-governance" / "_lib" / "ledger.py"
spec = importlib.util.spec_from_file_location("ledger_lib", ledger_py)
ledger_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger_lib)
Ledger = ledger_lib.Ledger


def test_ledger_append_and_verify_chain_valid(tmp_path):
    ledger_file = tmp_path / "ledger.jsonl"
    ledger = Ledger(ledger_file)

    # Append entries
    e1 = ledger.append("TEST_EVENT_1", "prime-agent", {"action": "step1"})
    e2 = ledger.append("TEST_EVENT_2", "builder-agent", {"action": "step2"})

    assert e1["prev_hash"] == "0" * 64
    assert e2["prev_hash"] == e1["hash"]

    # Verify chain
    res = ledger.verify_chain()
    assert res["status"] == "VALID"
    assert res["total_entries"] == 2
    assert res["chain_intact"] is True


def test_ledger_verify_chain_tampered(tmp_path):
    ledger_file = tmp_path / "ledger.jsonl"
    ledger = Ledger(ledger_file)

    ledger.append("TEST_EVENT_1", "prime-agent", {"action": "step1"})
    ledger.append("TEST_EVENT_2", "builder-agent", {"action": "step2"})

    # Tamper with entry 1 details
    lines = ledger_file.read_text().splitlines()
    tampered_entry = json.loads(lines[0])
    tampered_entry["details"]["action"] = "tampered_step1"
    lines[0] = json.dumps(tampered_entry)
    ledger_file.write_text("\n".join(lines) + "\n")

    res = ledger.verify_chain()
    assert res["status"] == "TAMPERED"
    assert res["corrupted_line"] == 1
    assert res["chain_intact"] is False


def test_ledger_verify_chain_legacy_fallback(tmp_path):
    ledger_file = tmp_path / "ledger.jsonl"
    # Write legacy entry without prev_hash or hash
    legacy_entry = {"sequence_id": 1, "event_type": "LEGACY", "agent_id": "prime-agent"}
    ledger_file.write_text(json.dumps(legacy_entry) + "\n")

    ledger = Ledger(ledger_file)
    res = ledger.verify_chain()
    assert res["status"] == "LEGACY_UNCHAINED"
    assert res["chain_intact"] is True
