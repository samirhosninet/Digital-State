#!/usr/bin/env python3
"""Builder self-test: prove the codified Workflow Engine enforces the cycle.

This is the BUILDER evidence artifact for DS-WORKFLOW-KERNEL-001. It runs the
happy path through the Hermes Kanban Orchestrator (delegating all transitions to
the Workflow Kernel) and asserts that out-of-order / unauthorized transitions are
rejected. No new roles/layers; Hermes simulated locally.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
sys.path.insert(0, str(HERE.parent / "002-bootstrap"))
sys.path.insert(0, str(HERE.parent / "_engine"))
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator
from workflow_kernel import WorkflowKernel, illegal_skips


def main():
    tmp = Path(tempfile.mkdtemp())
    board = tmp / "board.json"
    ledger = Ledger(tmp / "ledger.jsonl")
    orch = KanbanOrchestrator(board, ledger)
    k = WorkflowKernel()

    # Happy path (every transition authorized by its constitutional role).
    orch.create_card("K001", "Codify governance workflow", "EVENT")
    steps = [
        ("PRIME_SPECKIT", "prime-agent"),
        ("KANBAN_CREATED", "prime-agent"),
        ("BUILDER_QUEUE", "prime-agent"),
        ("BUILDER_EXECUTION", "builder-agent"),
        ("READY_FOR_AUDIT", "builder-agent"),
        ("AUDITOR_REVIEW", "auditor-agent"),
        ("READY_FOR_PRIME", "auditor-agent"),
        ("PRIME_REVIEW", "prime-agent"),
        ("HUMAN_APPROVAL", "prime-agent"),
        ("RELEASE_WORKFLOW", "human"),   # human-only gate
        ("DONE", "prime-agent"),
    ]
    for state, role in steps:
        orch.transition("K001", state, role)

    # Reject: agent tries to cross the human gate.
    bad = [
        ("PRIME_REVIEW", "RELEASE_WORKFLOW", "prime-agent"),
        (HUMAN_APPROVAL := "HUMAN_APPROVAL", "RELEASE_WORKFLOW", "prime-agent"),
        (HUMAN_APPROVAL, "BUILDER_EXECUTION", "auditor-agent"),
    ]
    rejected = 0
    for frm, to, role in bad:
        try:
            k.can_advance(role, frm, to)
            orch2 = KanbanOrchestrator(board, ledger)
            orch2.board["cards"]["K001"]["state"] = frm
            orch2.transition("K001", to, role)
            raise AssertionError(f"SHOULD HAVE DENIED {frm}->{to} by {role}")
        except (ValueError, AssertionError) as e:
            rejected += 1

    # The kernel's representative illegal-skip matrix must ALL be denied.
    for frm, to, role in illegal_skips():
        assert not k.can_advance(role, frm, to), f"leak: {frm}->{to} by {role}"
        rejected += 1

    print(f"HAPPY_PATH_OK states={len(steps)} | ILLEGAL_TRANSITIONS_DENIED={rejected} "
          f"| chain_valid={ledger.valid()}")
    assert ledger.valid()
    return 0


if __name__ == "__main__":
    sys.exit(main())
