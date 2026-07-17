# Feature Specification: DS-BOOTSTRAP-REAL-WORLD-001 (Bootstrap — Digital State self-application)

**Created**: 2026-07-17 | **Status**: Approved
**Input**: Turn Digital State from documents into a runnable system inside the workspace: a real Hermes-compatible Kanban Orchestrator as the execution workflow, driving the full lifecycle (Prime -> SpecKit -> Kanban -> Builder -> Auditor -> Prime -> Release).

> LIMITED, RECORDED EXCEPTION to the READ-ONLY Product Validation freeze (operator-ratified). No source-product change, no new roles/layers, no constitution/architecture change. Hermes execution is a SIMULATION (no live cluster in this env).

## User Story 1 (P1) — Digital State runs its own lifecycle
As the governance operator, I can drive the governance lifecycle end-to-end against a Digital State internal event using a runnable Kanban Orchestrator, proving the architecture works, not just on paper.
**Acceptance**: Orchestrator creates/assigns/transitions cards; every transition is mirrored to the hash-chained ledger; Builder+Auditor evidence is signed.

## User Story 2 (P1) — Observable release
As an external user, I can read a GitHub Release stating version + what changed + when.
**Acceptance**: Version bump, commit, tag, GitHub Release with notes.

## FR / SC mirrors DS-SELF-GOVERNANCE-001; all 5 success criteria required.
