import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

from digital_state.core.exceptions import EvidenceError


class AuditLogger:
    """Handles secure, append-only logging of all state transitions and policy decisions.
    
    Uses cryptographic hash chaining and sequential index verification (sequence_id)
    to guarantee log integrity and detect deletions or insertions.
    """

    def __init__(self, log_path: str):
        self.log_path = log_path
        self._ensure_log_exists()

    def _ensure_log_exists(self) -> None:
        """Create the directory and the log file if they do not exist."""
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                pass

    def _calculate_hash(self, entry: Dict[str, Any], prev_hash: str) -> str:
        """Calculate SHA-256 hash of the entry content combined with the previous hash."""
        entry_str = json.dumps(entry, sort_keys=True)
        hasher = hashlib.sha256()
        hasher.update(prev_hash.encode("utf-8"))
        hasher.update(entry_str.encode("utf-8"))
        return hasher.hexdigest()

    def _get_last_entry(self) -> Dict[str, Any]:
        """Read the last entry to get its hash and sequence_id."""
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return {"hash": "0" * 64, "sequence_id": 0}

        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return {"hash": "0" * 64, "sequence_id": 0}
            
            try:
                return json.loads(lines[-1].strip())
            except json.JSONDecodeError:
                return {"hash": "0" * 64, "sequence_id": 0}

    def append_entry(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new entry with cryptographic chaining and sequence validation."""
        last_entry = self._get_last_entry()
        prev_hash = last_entry.get("hash", "0" * 64)
        next_seq_id = last_entry.get("sequence_id", 0) + 1
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Base entry containing payload
        payload = {
            "sequence_id": next_seq_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
            "prev_hash": prev_hash
        }
        
        # Add hash of the payload
        entry_hash = self._calculate_hash(payload, prev_hash)
        full_entry = {**payload, "hash": entry_hash}

        tmp_path = self.log_path + ".tmp"
        try:
            existing_lines = []
            if os.path.exists(self.log_path):
                with open(self.log_path, "r", encoding="utf-8") as f:
                    existing_lines = f.readlines()

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.writelines(existing_lines)
                f.write(json.dumps(full_entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.log_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise EvidenceError(f"Failed to append entry atomically: {e}")

        return full_entry

    def verify_log_integrity(self) -> bool:
        """Verifies the integrity of the entire log chain, checking hashes and index sequence.
        
        Raises EvidenceError if any entry is modified, deleted, or out of sequence.
        """
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return True

        prev_hash = "0" * 64
        expected_seq_id = 1
        
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    raise EvidenceError(f"Log corruption at line {line_idx}: Invalid JSON.") from e
                
                # Check sequence ID continuity
                actual_seq_id = entry.get("sequence_id")
                if actual_seq_id != expected_seq_id:
                    raise EvidenceError(
                        f"Log integrity validation failed at line {line_idx}: "
                        f"Sequence ID gap. Expected index {expected_seq_id}, got {actual_seq_id}."
                    )
                
                expected_hash = entry.get("hash")
                payload = {
                    "sequence_id": entry.get("sequence_id"),
                    "timestamp": entry.get("timestamp"),
                    "event_type": entry.get("event_type"),
                    "agent_id": entry.get("agent_id"),
                    "details": entry.get("details"),
                    "prev_hash": entry.get("prev_hash")
                }
                
                # Check link to previous block
                if payload["prev_hash"] != prev_hash:
                    raise EvidenceError(
                        f"Log integrity validation failed at line {line_idx}: "
                        f"Hash chain broken. Expected prev_hash '{prev_hash}', got '{payload['prev_hash']}'."
                    )
                
                # Verify self hash
                actual_hash = self._calculate_hash(payload, prev_hash)
                if actual_hash != expected_hash:
                    raise EvidenceError(
                        f"Log integrity validation failed at line {line_idx}: "
                        f"Hash mismatch. Recomputed hash '{actual_hash}', stored hash '{expected_hash}'."
                    )
                
                # Advance pointers
                prev_hash = expected_hash
                expected_seq_id += 1
                
        return True

    def read_entries(self) -> List[Dict[str, Any]]:
        """Retrieve all entries in the audit log."""
        entries = []
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return entries

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries
