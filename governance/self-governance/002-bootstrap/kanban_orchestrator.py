#!/usr/bin/env python3
"""Hermes-compatible Kanban Orchestrator — local, runnable execution workflow.

A faithful LOCAL SIMULATION of the Hermes Kanban runtime (no live cluster exists
in this environment). Task-management semantics (create / assign / transition /
comment) are delegated to the codified Digital State Workflow Kernel
(governance/self-governance/_engine/workflow_kernel.py) as the SINGLE authority
for legal transitions — so chat is only an event-input interface, never the
workflow coordinator. Every change is persisted to board state + the
hash-chained governance ledger, signed by the acting agent.

Workflow (codified constitutional cycle):
  USER_SUBMITTED -> PRIME_SPECKIT -> KANBAN_CREATED -> BUILDER_QUEUE
  -> BUILDER_EXECUTION -> READY_FOR_AUDIT -> AUDITOR_REVIEW -> READY_FOR_PRIME
  -> PRIME_REVIEW -> HUMAN_APPROVAL -> RELEASE_WORKFLOW -> DONE
  (AUDITOR_REVIEW -> BUILDER_EXECUTION on Veto; HUMAN_APPROVAL -> BUILDER_EXECUTION
   on human Reject.)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
sys.path.insert(0, str(HERE.parent / "_engine"))
from ledger import Ledger
from workflow_kernel import WorkflowKernel, STATES as KERNEL_STATES

# Backward-compat alias for pre-006 boards (v1.5-v1.7).
LEGACY_STATES = ["SPEC_CREATED", "PLANNED", "TASK_CREATED", "BUILDER_ASSIGNED",
                 "IMPLEMENTATION", "AUDITOR_REVIEW", "PRIME_ACCEPTANCE"]
KERNEL = WorkflowKernel()
ALL_STATES = KERNEL_STATES + LEGACY_STATES


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

    @staticmethod
    def _legacy_state(state):
        # Map canonical kernel state -> legacy label for older boards.
        return {
            "PRIME_SPECKIT": "SPEC_CREATED", "KANBAN_CREATED": "PLANNED",
            "BUILDER_QUEUE": "TASK_CREATED", "BUILDER_ASSIGNED_LEG": "BUILDER_ASSIGNED",
            "BUILDER_EXECUTION": "IMPLEMENTATION", "READY_FOR_PRIME": "PRIME_ACCEPTANCE",
            "PRIME_REVIEW": "PRIME_ACCEPTANCE", "HUMAN_APPROVAL": "PRIME_ACCEPTANCE",
        }.get(state, state)

    def create_card(self, cid, title, gate, assignee=None):
        if cid in self.board["cards"]:
            raise ValueError(f"card {cid} already exists")
        self.board["cards"][cid] = {
            "id": cid, "title": title, "gate": gate, "state": "USER_SUBMITTED",
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

    def transition(self, cid, new_state, acting_role="prime-agent"):
        if new_state not in ALL_STATES:
            raise ValueError(f"unknown state {new_state}")
        c = self.board["cards"][cid]
        frm = c["state"]
        if frm == new_state:
            return c
        # Single enforcement point: delegate legality to the codified kernel.
        if not KERNEL.can_advance(acting_role, frm, new_state):
            raise ValueError(
                f"unauthorized transition {frm} -> {new_state} by {acting_role} "
                f"(human gate={KERNEL.HUMAN_GATE}; requires role "
                f"{KERNEL.authorized_role(frm, new_state) or 'human'})")
        c["state"] = new_state
        self._save()
        role = KERNEL.authorized_role(frm, new_state) or acting_role
        self._log("transition", role, {"card": cid, "to": new_state})
        self.ledger.append("STATE_TRANSITION", role,
                           {"gate": new_state, "card": cid, "status": "complete",
                            "authorized_by": role})
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
            print(f"{cid:8} {c['state']:18} @{c['assignee']}  {c['title']}")
        return self.board


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("usage: kanban_orchestrator.py <board.json> <cmd> [args...]")
        print("  create-card <id> <title> <gate>")
        print("  assign <id> <role> | transition <id> <STATE> [role] | comment <id> <role> <text> | show")
        sys.exit(2)
    board = Path(args[0])
    cmd = args[1]
    orch = KanbanOrchestrator(board, Ledger(board.parent / "ledger.jsonl"))
    if cmd == "create-card":
        orch.create_card(args[2], args[3], args[4])
    elif cmd == "assign":
        orch.assign(args[2], args[3])
    elif cmd == "transition":
        role = args[3] if len(args) <= 4 else args[4]
        orch.transition(args[2], args[3], role)
    elif cmd == "comment":
        orch.comment(args[2], args[3], " ".join(args[4:]))
    elif cmd == "show":
        orch.show()
    else:
        print("unknown cmd", cmd); sys.exit(2)
    print("chain valid:", orch.ledger.valid())


if __name__ == "__main__":
    main()
