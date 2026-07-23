"""Audit Log Projector for Digital State Observability (ORCHESTRATION-004).

Reads audit_log.jsonl in read-only mode outside FileLock boundaries to generate event streams.
"""

import json
import os
from typing import List, Dict, Any, Optional

from digital_state.observability.checkpoint import CheckpointManager
from digital_state.observability.engine import ProjectionEngine
from digital_state.observability.serializer import EventSerializer


class AuditLogProjector:
    """Decoupled, read-only event projector tailing audit_log.jsonl."""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.checkpoint_manager = CheckpointManager(self.workspace_root)
        self.engine = ProjectionEngine()
        self.serializer = EventSerializer()

    def get_log_path(self) -> str:
        """Resolves active path to memory/audit_log.jsonl or .specify/audit_log.jsonl."""
        specify_dir = os.path.join(self.workspace_root, ".specify")
        mem_path = os.path.join(specify_dir, "memory", "audit_log.jsonl")
        if os.path.exists(mem_path):
            return mem_path
        return os.path.join(specify_dir, "audit_log.jsonl")

    def get_unprojected_entries(self) -> List[Dict[str, Any]]:
        """Reads entries from audit_log.jsonl starting after last_sequence_id checkpoint."""
        log_path = self.get_log_path()
        if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
            return []

        checkpoint = self.checkpoint_manager.load_checkpoint()
        last_seq = checkpoint.get("last_sequence_id", 0)

        unprojected = []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("sequence_id", 0) > last_seq:
                            unprojected.append(entry)
                    except json.JSONDecodeError:
                        # Skip incomplete trailing lines during active file append
                        continue
        except Exception:
            return []

        return unprojected

    def project_new_events(self) -> List[Dict[str, Any]]:
        """Processes un-projected entries, updates offset checkpoints, and returns serialized events."""
        entries = self.get_unprojected_entries()
        projected = []
        for entry in entries:
            serialized = self.serializer.serialize_entry(entry)
            if serialized:
                projected.append(serialized)
                self.checkpoint_manager.save_checkpoint(
                    sequence_id=serialized["sequence_id"],
                    entry_hash=serialized["hash"],
                )
        return projected

    def search_events(
        self,
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        feature_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Queries entire audit history without modifying offset checkpoints."""
        log_path = self.get_log_path()
        if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
            return []

        all_entries = []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        all_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            return []

        return self.engine.filter_events(
            all_entries,
            event_type=event_type,
            agent_id=agent_id,
            feature_id=feature_id,
        )
