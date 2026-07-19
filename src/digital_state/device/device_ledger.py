"""Device Audit Ledger (v1.11.0-device).

Manages tamper-evident SHA-256 inter-line chained audit log for local device execution events:
    .specify/device/device_ledger.jsonl

Hash chain formula:
    current_hash = SHA256(previous_hash + canonical_json(event_payload))
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


class DeviceLedger:
    """Local device audit log manager with SHA-256 inter-line hash chaining."""

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or Path(".specify") / "device" / "device_ledger.jsonl"
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _canon(data: Dict[str, Any]) -> str:
        """Produces canonical JSON string for SHA-256 digest calculation."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def get_last_hash(self) -> str:
        """Retrieves current tail hash from device_ledger.jsonl (defaults to 64 zeros)."""
        if not self.ledger_path.exists():
            return "0" * 64
        lines = [line.strip() for line in self.ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return "0" * 64
        try:
            last_entry = json.loads(lines[-1])
            return last_entry.get("current_hash") or last_entry.get("hash") or "0" * 64
        except Exception:
            return "0" * 64

    def append(self, trace_id: str, decision: Dict[str, Any], policy_version: str = "v1.11.0-p1") -> Dict[str, Any]:
        """Appends a new hash-chained event to device_ledger.jsonl."""
        prev_hash = self.get_last_hash()
        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "decision": decision,
            "policy_version": policy_version,
            "previous_hash": prev_hash
        }

        # Calculate current_hash = SHA256(previous_hash + canonical_payload)
        to_hash = (prev_hash + self._canon(payload)).encode("utf-8")
        current_hash = hashlib.sha256(to_hash).hexdigest()
        payload["current_hash"] = current_hash

        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        return payload

    def verify_chain(self) -> Dict[str, Any]:
        """Verifies line-by-line SHA-256 hash chain continuity of device_ledger.jsonl."""
        if not self.ledger_path.exists():
            return {"status": "VALID", "total_entries": 0, "chain_intact": True}

        lines = [line.strip() for line in self.ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return {"status": "VALID", "total_entries": 0, "chain_intact": True}

        expected_prev = "0" * 64
        for idx, line in enumerate(lines, start=1):
            try:
                entry = json.loads(line)
            except Exception:
                return {"status": "CORRUPTED_JSON", "corrupted_line": idx, "chain_intact": False}

            prev_hash = entry.get("previous_hash")
            current_hash = entry.get("current_hash")

            if prev_hash != expected_prev:
                return {
                    "status": "TAMPERED",
                    "corrupted_line": idx,
                    "reason": f"Previous hash mismatch at line {idx}",
                    "chain_intact": False
                }

            # Recalculate hash
            check_payload = {
                "trace_id": entry["trace_id"],
                "timestamp": entry["timestamp"],
                "decision": entry["decision"],
                "policy_version": entry["policy_version"],
                "previous_hash": prev_hash
            }
            recalculated = hashlib.sha256((prev_hash + self._canon(check_payload)).encode("utf-8")).hexdigest()

            if recalculated != current_hash:
                return {
                    "status": "TAMPERED",
                    "corrupted_line": idx,
                    "reason": f"Hash signature mismatch at line {idx}",
                    "chain_intact": False
                }

            expected_prev = current_hash

        return {"status": "VALID", "total_entries": len(lines), "chain_intact": True}
