"""Unit tests for DeviceDaemon local IPC communication and Fail-Closed behavior (v1.11.0-device)."""

import time
from pathlib import Path
from digital_state.device.device_daemon import DeviceDaemon
from digital_state.device.evidence import EvidenceBundleManager


def test_device_daemon_local_ipc_flow(tmp_path):
    device_dir = tmp_path / "device"
    evidence_mgr = EvidenceBundleManager(device_dir=device_dir)
    evidence_mgr.generate_bundle(last_sync_timestamp=time.time())

    daemon = DeviceDaemon(device_dir=device_dir, port=49822)
    daemon.start(background=True)

    time.sleep(0.1)

    # Valid IPC Request
    req = {
        "trace_id": "IPC-01",
        "tool_name": "execute_command",
        "agent_id": "agent-test"
    }
    resp = DeviceDaemon.send_ipc_request(req, port=49822)
    assert resp["action"] == "approve"
    assert resp["trace_id"] == "IPC-01"

    daemon.stop()


def test_device_daemon_unavailable_fail_closed():
    # Attempting IPC to non-existent daemon port -> Fail-Closed BLOCK
    req = {
        "trace_id": "IPC-FAIL",
        "tool_name": "execute_command",
        "agent_id": "agent-test"
    }
    resp = DeviceDaemon.send_ipc_request(req, port=59999)
    assert resp["action"] == "block"
    assert "Fail-Closed" in resp["reason"] or "unavailable" in resp["reason"]
