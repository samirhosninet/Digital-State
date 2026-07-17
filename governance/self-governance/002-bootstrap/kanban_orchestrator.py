#!/usr/bin/env python3
"""Hermes-compatible Kanban Orchestrator — local, runnable execution workflow.

A faithful LOCAL SIMULATION of the Hermes Kanban runtime (no live cluster exists
in this environment). It provides the task-management semantics the governance
lifecycle drives (create / assign / transition / comment / complete) and persists
every change to board state plus the hash-chained governance ledger, signed by the
acting agent. Each state transition is also mirrored as a lifecycle gate entry,
so the board and the immutable audit trail never drift.

Workflow states:
  SPEC_CREATED -> PLANNED -> TASK_CREATED -> BUILDER_ASSIGNED
  -> IMPLEMENTATION -> AUDITOR_REVIEW -> PRIME_ACCEPTANCE
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
from ledger import Ledger

STATES = [
    "SPEC_CREATED", "PLANNED", "TASK_CREATED", "BUILDER_ASSIGNED",
    "IMPLEMENTATION", "AUDITOR_REVIEW", "PRIME_ACCEPTANCE",
]
# Which agent is authorized to drive each transition (role segregation).
ROLE = {
    "SPEC_CREATED": "prime-agent", "PLANNED": "prime-agent", "TASK_CREATED": "prime-agent",
    "BUILDER_ASSIGNED": "prime-agent", "IMPLEMENTATION": "builder-agent",
    "AUDITOR_REVIEW": "auditor-agent", "PRIME_ACCEPTANCE": "prime-agent",
}


class KanbanOrchestrator:
    def __init__(self, board_path: Path, ledger: Ledger):
        self.board_path = Path(board_path)
        self.ledger = ledger
        self.board = self._load()

    def _load(self):
        if self.board_path.exists():
            return json.loads(self.board_path.read_text())
        return {"cards": {}, "history": []}

    def _save(self):
        self.board_path.write_text(json.dumps(self.board, indent=2))

    def _log(self, action, role, detail):
        self.ledger.append("KANBAN", role, {"action": action, **detail})
        self.board["history"].append({
            "ts": datetime.now(timezone.utc).isoformat(), "action": action, "by": role, **detail
        })
        self._save()

    def create_card(self, cid, title, gate, assignee=None):
        if cid in self.board["cards"]:
            raise ValueError(f"card {cid} already exists")
        self.board["cards"][cid] = {
            "id": cid, "title": title, "gate": gate, "state": "SPEC_CREATED",
            "assignee": assignee, "comments": [],
        }
        self._save()
        self._log("create_card", "prime-agent", {"card": cid, "title": title, "gate": gate})
        return self.board["cards"][cid]

    def assign(self, cid, role):
        self.board["cards"][cid]["assignee"] = role
        self._save()
        self._log("assign", "prime-agent", {"card": cid, "to": role})
        return self.board["cards"][cid]

    def transition(self, cid, new_state):
        if new_state not in STATES:
            raise ValueError(f"unknown state {new_state}")
        c = self.board["cards"][cid]
        if STATES.index(new_state) != STATES.index(c["state"]) + 1:
            raise ValueError(f"illegal transition {c['state']} -> {new_state}")
        c["state"] = new_state
        self._save()
        role = ROLE[new_state]
        self._log("transition", role, {"card": cid, "to": new_state})
        # Mirror into the lifecycle ledger as a governance gate.
        self.ledger.append("STATE_TRANSITION", role, {"gate": new_state, "card": cid, "status": "complete"})
        return c

    def comment(self, cid, role, text):
        self.board["cards"][cid]["comments"].append({
            "by": role, "text": text, "ts": datetime.now(timezone.utc).isoformat()
        })
        self._save()
        self._log("comment", role, {"card": cid, "text": text})
        return self.board["cards"][cid]

    def show(self):
        for cid, c in self.board["cards"].items():
            print(f"{cid:8} {c['state']:16} @{c['assignee']}  {c['title']}")
        return self.board


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("usage: kanban_orchestrator.py <board.json> <cmd> [args...]")
        print("  create-card <id> <title> <gate>")
        print("  assign <id> <role> | transition <id> <STATE> | comment <id> <role> <text> | show")
        sys.exit(2)
    board = Path(args[0])
    cmd = args[1]
    orch = KanbanOrchestrator(board, Ledger(board.parent / "ledger.jsonl"))
    if cmd == "create-card":
        orch.create_card(args[2], args[3], args[4])
    elif cmd == "assign":
        orch.assign(args[2], args[3])
    elif cmd == "transition":
        orch.transition(args[2], args[3])
    elif cmd == "comment":
        orch.comment(args[2], args[3], " ".join(args[4:]))
    elif cmd == "show":
        orch.show()
    else:
        print("unknown cmd", cmd); sys.exit(2)
    print("chain valid:", orch.ledger.valid())


if __name__ == "__main__":
    main()
