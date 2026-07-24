"""Kanban Engine for Prime Operating Model (v2.0).

Parses tasks.md into a machine-readable Kanban board (.specify/kanban/board.json)
and manages card lifecycle state transitions (TODO -> IN_PROGRESS -> IN_REVIEW -> DONE).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class KanbanCard:
    """Represents an atomic, scoped Kanban task card."""

    def __init__(
        self,
        card_id: str,
        title: str,
        dependencies: Optional[List[str]] = None,
        allowed_file_scope: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        status: str = "TODO",
        assigned_agent: str = "builder-agent",
        verifier_agent: str = "auditor-agent",
        evidence_hash: str = "",
    ):
        self.card_id = card_id
        self.title = title
        self.dependencies = dependencies or []
        self.allowed_file_scope = allowed_file_scope or []
        self.acceptance_criteria = acceptance_criteria or []
        self.status = status
        self.assigned_agent = assigned_agent
        self.verifier_agent = verifier_agent
        self.evidence_hash = evidence_hash

    def to_dict(self) -> Dict[str, Any]:
        """Converts card object to JSON dictionary."""
        return {
            "id": self.card_id,
            "title": self.title,
            "dependencies": self.dependencies,
            "allowed_file_scope": self.allowed_file_scope,
            "acceptance_criteria": self.acceptance_criteria,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "verifier_agent": self.verifier_agent,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KanbanCard":
        """Instantiates card from JSON dictionary."""
        return cls(
            card_id=data["id"],
            title=data.get("title", ""),
            dependencies=data.get("dependencies", []),
            allowed_file_scope=data.get("allowed_file_scope", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            status=data.get("status", "TODO"),
            assigned_agent=data.get("assigned_agent", "builder-agent"),
            verifier_agent=data.get("verifier_agent", "auditor-agent"),
            evidence_hash=data.get("evidence_hash", ""),
        )


class KanbanEngine:
    """Manages Kanban board compilation, card state transitions, and dependency dispatching."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.specify_dir = self.workspace_root / ".specify"
        self.kanban_dir = self.specify_dir / "kanban"
        self.board_path = self.kanban_dir / "board.json"

    def ensure_directories(self) -> None:
        """Ensures .specify/kanban directory exists."""
        self.kanban_dir.mkdir(parents=True, exist_ok=True)

    def parse_tasks_md(self, tasks_md_path: Path) -> List[KanbanCard]:
        """Parses tasks.md markdown file into a list of KanbanCard objects."""
        if not tasks_md_path.exists():
            return []

        content = tasks_md_path.read_text(encoding="utf-8")
        cards: List[KanbanCard] = []

        # Matches task headers or task bullet points: e.g. - [ ] [TASK-001] Title or ### [TASK-001] Title
        task_pattern = re.compile(
            r"(?:-\s*\[[ xX]\]|###)\s*\[(TASK-\d+)\]\s*(.+)", re.MULTILINE
        )
        matches = task_pattern.findall(content)

        for card_id, title in matches:
            cards.append(
                KanbanCard(
                    card_id=card_id.strip(),
                    title=title.strip(),
                    status="TODO",
                )
            )

        # Fallback for generic numbered or bulleted tasks if explicit TASK-XXX pattern is absent
        if not cards:
            lines = content.splitlines()
            task_idx = 1
            for line in lines:
                line_str = line.strip()
                if line_str.startswith("- [ ]") or line_str.startswith("* "):
                    clean_title = re.sub(r"^(-\s*\[[ xX]\]|\*\s*)", "", line_str).strip()
                    if clean_title:
                        cards.append(
                            KanbanCard(
                                card_id=f"TASK-{task_idx:03d}",
                                title=clean_title,
                                status="TODO",
                            )
                        )
                        task_idx += 1

        return cards

    def compile_board(self, tasks_md_path: Path) -> Dict[str, Any]:
        """Compiles tasks.md into .specify/kanban/board.json."""
        self.ensure_directories()
        cards = self.parse_tasks_md(tasks_md_path)
        now_iso = datetime.now(timezone.utc).isoformat()

        board_data = {
            "$schema": "https://digitalstate.io/schemas/kanban.v2.json",
            "project_id": "DS-V2-PROJECT",
            "source_artifact": str(tasks_md_path),
            "generated_at": now_iso,
            "total_cards": len(cards),
            "columns": ["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"],
            "cards": [c.to_dict() for c in cards],
        }

        with open(self.board_path, "w", encoding="utf-8") as f:
            json.dump(board_data, f, indent=2)

        return board_data

    def load_board(self) -> Optional[Dict[str, Any]]:
        """Loads existing board.json from disk."""
        if not self.board_path.exists():
            return None
        try:
            with open(self.board_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def get_unblocked_cards(self) -> List[KanbanCard]:
        board = self.load_board()
        if not board:
            return []
        cards = [KanbanCard.from_dict(c) for c in board.get("cards", [])]
        done_ids = {c.card_id for c in cards if c.status == "DONE"}
        return [c for c in cards if c.status == "TODO" and all(dep in done_ids for dep in c.dependencies)]

    def get_next_dispatchable_card(self) -> Optional[KanbanCard]:
        """Returns the highest priority TODO card whose dependencies are all DONE."""
        board = self.load_board()
        if not board:
            return None

        cards = [KanbanCard.from_dict(c) for c in board.get("cards", [])]
        done_ids = {c.card_id for c in cards if c.status == "DONE"}

        # Invariant: Only dispatch if no card is currently IN_PROGRESS or IN_REVIEW
        active = [c for c in cards if c.status in ("IN_PROGRESS", "IN_REVIEW")]
        if active:
            return None

        for card in cards:
            if card.status == "TODO":
                # Check if dependencies are all satisfied
                if all(dep in done_ids for dep in card.dependencies):
                    return card
        return None

    def update_card_status(
        self, card_id: str, new_status: str, evidence_hash: str = ""
    ) -> bool:
        """Updates the status of a specific card on the board."""
        board = self.load_board()
        if not board:
            return False

        updated = False
        for card_data in board.get("cards", []):
            if card_data["id"] == card_id:
                card_data["status"] = new_status
                if evidence_hash:
                    card_data["evidence_hash"] = evidence_hash
                updated = True
                break

        if updated:
            with open(self.board_path, "w", encoding="utf-8") as f:
                json.dump(board, f, indent=2)
            return True
        return False
