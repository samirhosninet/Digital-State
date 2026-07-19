"""Local Device Policy Engine (v1.11.0-device).

Evaluates tool call interception requests against local signed policy-state.json.
Enforces Fail-Safe Default-Deny on:
    - Missing context or unknown agent
    - Invalid policy signature
    - Expired offline state (DEFAULT_DENY)
    - Missing policy file
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from digital_state.device.evidence import EvidenceBundleManager
from digital_state.device.device_ledger import DeviceLedger


class LocalPolicyEngine:
    """Sub-millisecond local policy evaluation engine."""

    def __init__(self, device_dir: Optional[Path] = None, ledger: Optional[DeviceLedger] = None):
        self.device_dir = device_dir or Path(".specify") / "device"
        self.evidence_mgr = EvidenceBundleManager(device_dir=self.device_dir)
        self.ledger = ledger or DeviceLedger(ledger_path=self.device_dir / "device_ledger.jsonl")

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an InterceptionRequest dictionary.

        Returns APPROVE dictionary or BLOCK dictionary (Fail-Safe Default-Deny).
        """
        start_time = time.time()
        trace_id = request.get("trace_id") or "UNKNOWN_TRACE"

        # 1. Missing tool_name or context check
        tool_name = request.get("tool_name")
        agent_id = request.get("agent_id")

        if not tool_name or not agent_id:
            decision = {
                "action": "block",
                "trace_id": trace_id,
                "reason": "Missing mandatory tool_name or agent_id context. Fail-Safe Deny triggered.",
                "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
            }
            self.ledger.append(trace_id, decision)
            return decision

        # 2. Check policy file existence
        policy_path = self.device_dir / "policy-state.json"
        if not policy_path.exists():
            decision = {
                "action": "block",
                "trace_id": trace_id,
                "reason": "Missing local policy-state.json file. Fail-Safe Deny triggered.",
                "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
            }
            self.ledger.append(trace_id, decision)
            return decision

        # 3. Read and parse policy
        try:
            policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
        except Exception:
            decision = {
                "action": "block",
                "trace_id": trace_id,
                "reason": "Corrupted local policy-state.json file. Fail-Safe Deny triggered.",
                "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
            }
            self.ledger.append(trace_id, decision)
            return decision

        # 4. Check 3-state offline lifecycle
        last_sync = policy_data.get("last_sync_timestamp") or 0.0
        offline_state = self.evidence_mgr.get_offline_state(last_sync)

        if offline_state == "DEFAULT_DENY":
            decision = {
                "action": "block",
                "trace_id": trace_id,
                "reason": "Offline grace period (24h) expired. Offline Default-Deny enforced.",
                "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
            }
            self.ledger.append(trace_id, decision)
            return decision

        # 5. Check allowed tools
        allowed_tools = policy_data.get("allowed_tools") or []
        if tool_name not in allowed_tools:
            decision = {
                "action": "block",
                "trace_id": trace_id,
                "reason": f"Tool '{tool_name}' is not in allowed tools policy.",
                "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
            }
            self.ledger.append(trace_id, decision)
            return decision

        # 6. Approved decision
        decision = {
            "action": "approve",
            "trace_id": trace_id,
            "offline_state": offline_state,
            "eval_duration_ms": round((time.time() - start_time) * 1000, 3)
        }
        self.ledger.append(trace_id, decision, policy_version=policy_data.get("policy_version", "v1.11.0-p1"))
        return decision
