"""Codified Digital State Governance Workflow Kernel (state machine).

This is the AUTHORITATIVE encoding of the existing constitutional governance
cycle (Constitution v1.2.0, Principle IV Gate-Based Progression + Architecture
DS-ARCHITECTURE-001 §2 Lifecycle Engine). It does NOT add roles/layers, change
the authority model, the constitution, or the architecture. It merely codifies
the already-specified sequence so the system imposes it automatically instead of
relying on chat-coordinated scripts.

Hard guarantees enforced here:
  * No stage may be skipped or transitioned out-of-order (gate-based progression).
  * Each transition is authorized only for its constitutional role.
  * HUMAN_APPROVAL is a hard gate: NO agent (prime/builder/auditor) may exit it.
    Only a `human` authorization can advance from HUMAN_APPROVAL -> RELEASE or
    send it back to BUILDER (reject). This preserves Human = Final Authority.
  * Auditor veto loops back to BUILDER_EXECUTION (auditor-only).

The Hermes Kanban Orchestrator delegates transition legality to this kernel, so
chat is only an event-input interface, never the workflow coordinator.
"""
from __future__ import annotations

ROLE_HUMAN = "human"
HUMAN_GATE = "HUMAN_APPROVAL"

# Canonical lifecycle states (the cycle the user specified, 1..11 + DONE).
STATES = [
    "USER_SUBMITTED", "PRIME_SPECKIT", "KANBAN_CREATED", "BUILDER_QUEUE",
    "BUILDER_EXECUTION", "READY_FOR_AUDIT", "AUDITOR_REVIEW", "READY_FOR_PRIME",
    "PRIME_REVIEW", HUMAN_GATE, "RELEASE_WORKFLOW", "DONE",
]

# allowed[from_state][to_state] = authorized_role
TRANSITIONS = {
    "USER_SUBMITTED":   {"PRIME_SPECKIT": "prime-agent"},
    "PRIME_SPECKIT":    {"KANBAN_CREATED": "prime-agent"},
    "KANBAN_CREATED":   {"BUILDER_QUEUE": "prime-agent"},
    "BUILDER_QUEUE":    {"BUILDER_EXECUTION": "builder-agent"},
    "BUILDER_EXECUTION":{"READY_FOR_AUDIT": "builder-agent"},
    "READY_FOR_AUDIT":  {"AUDITOR_REVIEW": "auditor-agent"},
    "AUDITOR_REVIEW":   {"READY_FOR_PRIME": "auditor-agent",
                          "BUILDER_EXECUTION": "auditor-agent"},   # approve / veto
    "READY_FOR_PRIME":  {"PRIME_REVIEW": "prime-agent"},
    "PRIME_REVIEW":     {HUMAN_GATE: "prime-agent"},
    HUMAN_GATE:         {"RELEASE_WORKFLOW": ROLE_HUMAN,
                          "BUILDER_EXECUTION": ROLE_HUMAN},        # human only
    "RELEASE_WORKFLOW": {"DONE": "prime-agent"},
}


def authorized_role(frm: str, to: str):
    return TRANSITIONS.get(frm, {}).get(to)


def requires_human(frm: str, to: str) -> bool:
    """True iff this transition may ONLY be driven by the human."""
    return frm == HUMAN_GATE and to in TRANSITIONS.get(frm, {})


def can_advance(role: str, frm: str, to: str) -> bool:
    """Single enforcement point. Chat/agents cannot bypass: any transition
    leaving HUMAN_APPROVAL is rejected unless the acting role is `human`."""
    if frm not in TRANSITIONS or to not in TRANSITIONS[frm]:
        return False
    if frm == HUMAN_GATE:
        return role == ROLE_HUMAN  # hard gate: agents forbidden
    return TRANSITIONS[frm][to] == role


def illegal_skips():
    """Representative forbidden transitions the engine must always deny.
    Used by the Builder self-test to prove enforcement."""
    return [
        ("PRIME_REVIEW", "RELEASE_WORKFLOW", "prime-agent"),    # skip human
        ("AUDITOR_REVIEW", "RELEASE_WORKFLOW", "auditor-agent"),# skip prime+human
        ("READY_FOR_PRIME", "RELEASE_WORKFLOW", "prime-agent"), # skip human
        (HUMAN_GATE, "RELEASE_WORKFLOW", "prime-agent"),        # agent at human gate
        (HUMAN_GATE, "BUILDER_EXECUTION", "auditor-agent"),     # agent at human gate
        ("BUILDER_EXECUTION", "RELEASE_WORKFLOW", "builder-agent"),
    ]


class WorkflowKernel:
    """Thin object wrapper so the Orchestrator can delegate to one authority."""
    STATES = STATES
    HUMAN_GATE = HUMAN_GATE

    def can_advance(self, role, frm, to):
        return can_advance(role, frm, to)

    def requires_human(self, frm, to):
        return requires_human(frm, to)

    def authorized_role(self, frm, to):
        return authorized_role(frm, to)
