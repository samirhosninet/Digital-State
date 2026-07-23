"""Checkpoint Manager for Digital State Observability (ORCHESTRATION-004).

Persists and retrieves offset checkpoints in .specify/observability_checkpoint.json.
"""

import json
import os
from typing import Dict, Any


class CheckpointManager:
    """Manages sequence_id offset checkpoints for idempotent event projection."""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.specify_dir = os.path.join(self.workspace_root, ".specify")
        self.checkpoint_file = os.path.join(self.specify_dir, "observability_checkpoint.json")

    def _ensure_dir(self) -> None:
        if not os.path.exists(self.specify_dir):
            os.makedirs(self.specify_dir, exist_ok=True)

    def load_checkpoint(self) -> Dict[str, Any]:
        """Loads offset checkpoint from disk."""
        if not os.path.exists(self.checkpoint_file):
            return {"last_sequence_id": 0, "last_hash": "0" * 64}
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "last_sequence_id": data.get("last_sequence_id", 0),
                    "last_hash": data.get("last_hash", "0" * 64),
                }
        except Exception:
            return {"last_sequence_id": 0, "last_hash": "0" * 64}

    def save_checkpoint(self, sequence_id: int, entry_hash: str) -> None:
        """Saves current sequence_id offset checkpoint atomically."""
        self._ensure_dir()
        data = {
            "last_sequence_id": sequence_id,
            "last_hash": entry_hash,
        }
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
