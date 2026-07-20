"""Unit tests for Local Policy Engine and Default-Deny enforcement (v1.11.0-device)."""

import json
import time
from pathlib import Path
from digital_state.device.policy_engine import LocalPolicyEngine
from digital_state.device.evidence import EvidenceBundleManager


def test_policy_engine_missing_context_or_file(tmp_path):
    device_dir = tmp_path / "device"
    engine = LocalPolicyEngine(device_dir=device_dir)

    # 1. Missing context -> BLOCK
    res0 = engine.evaluate({"trace_id": "T-01"})
    assert res0["action"] == "block"
    assert "Missing mandatory" in res0["reason"]

    # 2. Missing policy-state.json file -> BLOCK
    res1 = engine.evaluate({"trace_id": "T-02", "tool_name": "execute_command", "agent_id": "agent-1"})
    assert res1["action"] == "block"
    assert "Missing local policy-state.json" in res1["reason"]


def test_policy_engine_allowed_tool_and_offline_expiration(tmp_path):
    device_dir = tmp_path / "device"
    evidence_mgr = EvidenceBundleManager(device_dir=device_dir)

    # Create active policy bundle
    now_ts = time.time()
    evidence_mgr.generate_bundle(last_sync_timestamp=now_ts)

    engine = LocalPolicyEngine(device_dir=device_dir)

    # 1. Allowed tool call -> APPROVE
    req_allowed = {
        "trace_id": "T-03",
        "tool_name": "execute_command",
        "agent_id": "agent-1"
    }
    res_allowed = engine.evaluate(req_allowed)
    assert res_allowed["action"] == "approve"
    assert res_allowed["offline_state"] == "ACTIVE"

    # 2. Disallowed tool call -> BLOCK
    req_disallowed = {
        "trace_id": "T-04",
        "tool_name": "forbidden_unauthorized_tool",
        "agent_id": "agent-1"
    }
    res_disallowed = engine.evaluate(req_disallowed)
    assert res_disallowed["action"] == "block"
    assert "not in allowed tools" in res_disallowed["reason"]

    # 3. Expired offline state (>24h) -> BLOCK (DEFAULT_DENY)
    old_ts = now_ts - 100000  # > 24 hours ago
    evidence_mgr.generate_bundle(last_sync_timestamp=old_ts)

    res_expired = engine.evaluate(req_allowed)
    assert res_expired["action"] == "block"
    assert "Offline Grace Period" in res_expired["reason"] or "Offline grace period" in res_expired["reason"]
