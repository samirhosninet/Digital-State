"""Event Serializer for Digital State Observability (ORCHESTRATION-004).

Validates entry sequence integrity and formats structured audit projections.
"""

import json
import hashlib
from typing import Dict, Any, Optional


class EventSerializer:
    """Formats and validates projected audit log entries."""

    @staticmethod
    def calculate_hash(payload: Dict[str, Any], prev_hash: str) -> str:
        """Computes SHA-256 integrity hash matching AuditLogger schema."""
        entry_str = json.dumps(payload, sort_keys=True)
        hasher = hashlib.sha256()
        hasher.update(prev_hash.encode("utf-8"))
        hasher.update(entry_str.encode("utf-8"))
        return hasher.hexdigest()

    def serialize_entry(self, raw_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validates and formats a raw audit entry dictionary."""
        if not isinstance(raw_entry, dict):
            return None

        required_keys = {"sequence_id", "timestamp", "event_type", "agent_id", "details", "hash"}
        if not required_keys.issubset(raw_entry.keys()):
            return None

        return {
            "sequence_id": raw_entry["sequence_id"],
            "timestamp": raw_entry["timestamp"],
            "event_type": raw_entry["event_type"],
            "agent_id": raw_entry["agent_id"],
            "details": raw_entry["details"],
            "prev_hash": raw_entry.get("prev_hash", "0" * 64),
            "hash": raw_entry["hash"],
        }
