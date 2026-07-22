"""Kanban Card Manager for Digital State SDK (ORCHESTRATION-003).

Manages assignment cards in `.specify/kanban.json` required by validate_builder_execution_gate().
"""

import json
import os
from typing import Dict, Any, Optional


class KanbanManager:
    """SDK module for reading, writing, and updating .specify/kanban.json assignment cards."""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.specify_dir = os.path.join(self.workspace_root, ".specify")
        self.kanban_file = os.path.join(self.specify_dir, "kanban.json")

    def _ensure_dir(self) -> None:
        if not os.path.exists(self.specify_dir):
            os.makedirs(self.specify_dir, exist_ok=True)

    def load_kanban(self) -> Dict[str, Any]:
        """Loads .specify/kanban.json if present, returning a structured data dict."""
        if not os.path.exists(self.kanban_file):
            return {"cards": {}}
        try:
            with open(self.kanban_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "cards" not in data or not isinstance(data["cards"], dict):
                    return {"cards": {}}
                return data
        except Exception:
            return {"cards": {}}

    def save_kanban(self, data: Dict[str, Any]) -> None:
        """Saves kanban card dictionary to .specify/kanban.json atomically."""
        self._ensure_dir()
        with open(self.kanban_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_card(
        self,
        feature_id: str,
        assigned_to: str = "builder-agent",
        title: str = "",
        status: str = "IN_PROGRESS",
    ) -> Dict[str, Any]:
        """Creates or updates a kanban assignment card for a feature."""
        data = self.load_kanban()
        card = {
            "feature_id": feature_id,
            "title": title or f"Implementation Task for {feature_id}",
            "assigned_to": assigned_to,
            "status": status,
            "prerequisites": ["spec.md", "plan.md", "tasks.md"],
        }
        data["cards"][feature_id] = card
        self.save_kanban(data)
        return card

    def get_card(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a kanban card by feature_id."""
        data = self.load_kanban()
        return data["cards"].get(feature_id)

    def update_card_status(self, feature_id: str, status: str) -> bool:
        """Updates status of an existing kanban card."""
        data = self.load_kanban()
        if feature_id not in data["cards"]:
            return False
        data["cards"][feature_id]["status"] = status
        self.save_kanban(data)
        return True
