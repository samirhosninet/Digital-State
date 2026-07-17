# Feature Specification: Self-Governance Validation Cycle (DS-SELF-GOVERNANCE-001)

**Feature Branch**: `governance/self-governance/001-self-governance`
**Created**: 2026-07-18
**Status**: Draft → Approved
**Input**: User description: "Apply the Digital State lifecycle to itself to prove the governance path works end-to-end before using Digital State to govern the Hermes execution runtime."

> **Governance Exception Notice**: This artifact is created under a *limited, recorded exception* to the standing READ-ONLY Product Validation directive (carved by operator card `DS-SELF-GOVERNANCE-001`, ratified by Prime). It is **governance self-validation, not product change** — no source/runtime/architecture edits, no constitution change, no new roles/layers, no authority-model change. All assets live under `governance/self-governance/` so the frozen production baseline (`specs/`, `src/`, `framework/`, `integrations/`, `release/`) is untouched. Hermes execution in this environment is a **simulation** (no live cluster, no `gh` CLI); see Auditor findings.

## User Scenarios & Testing

### User Story 1 - Prove the governance path runs on itself (Priority: P1)

As the governance operator (Prime), I can drive the full `Prime → Spec → Plan → Tasks → Kanban → Builder → Auditor → Acceptance → Workspace Update → Release` path against a Digital State internal change, so the lifecycle is demonstrated to be real and executable rather than only described.

**Why this priority**: The request's entire point is to *prove* the internal lifecycle works before governing external Hermes execution. If this cannot be demonstrated, the final goal fails.

**Independent Test**: Execute every gate in sequence with a real artifact at each step and a hash-chained audit entry; confirm no gate is skipped and the Auditor gate is independent of the Builder.

**Acceptance Scenarios**:
1. **Given** the operator authorizes `DS-SELF-GOVERNANCE-001`, **When** Prime issues ALLOW and logs the freeze exception, **Then** a SpecKit `spec.md` exists and is recorded in the event ledger.
2. **Given** the spec is approved, **When** `plan.md` and `tasks.md` are produced, **Then** each carries a Constitution Check that passes with zero violations.
3. **Given** tasks exist, **When** Builder executes and Auditor verifies independently, **Then** both emit *signed* evidence and no agent self-approves its own work.

---

### User Story 2 - Workspace baseline advances with a verifiable release (Priority: P1)

As a downstream user, I can read the released state and know *what version, what changed, when* — so the self-governance cycle yields a real, traceable baseline increment.

**Why this priority**: The operator requires Version Increment + Commit + Tag + Release Notes. Without a verifiable release the cycle is not "complete" per the success criteria.

**Independent Test**: After acceptance, a version bump, a git commit, and a git tag exist locally; GitHub Release notes are prepared. Confirms the baseline is reproducible.

**Acceptance Scenarios**:
1. **Given** Prime signs off, **When** Workspace Update runs, **Then** `pyproject.toml` version is incremented and a git commit + tag are created.
2. **Given** the tag exists, **When** release notes are drafted, **Then** they cite the exact commit/tag and the event ledger as evidence.

---

### Edge Cases
- What happens when Hermes is not live? → The cycle uses a *simulated* Kanban and records this honestly; it does NOT claim live enforcement (spec 009 US2 constraint).
- What happens if Auditor vetoes? → The cycle halts at VERIFICATION; no Workspace Update or release.
- What happens if the freeze exception is absent? → Prime must DENY; no artifacts are created.

## Requirements

### Functional Requirements
- **FR-001**: System MUST produce a SpecKit `spec.md`, `plan.md`, and `tasks.md` for the event.
- **FR-002**: The `plan.md` MUST include a Constitution Check gate that passes with zero complexity violations.
- **FR-003**: Builder execution MUST produce *real* evidence (the existing test suite must pass) — not prose.
- **FR-004**: Auditor verification MUST be independent and emit a signature; Auditor MUST hold veto authority over the VERIFICATION gate.
- **FR-005**: Prime acceptance MUST be a recorded, signed gate decision.
- **FR-006**: Workspace Update MUST increment version + create a git commit + create a git tag.
- **FR-007**: Every lifecycle transition MUST append a hash-chained entry to the event ledger.

### Key Entities
- **GovernanceEvent**: `DS-SELF-GOVERNANCE-001` — the authorized exception record.
- **EventLedger**: hash-chained JSONL under `governance/self-governance/001-self-governance/ledger.jsonl`.
- **KanbanCard**: simulated task card under `governance/self-governance/001-self-governance/kanban.json`.

## Success Criteria

### Measurable Outcomes
- **SC-001**: All 7 lifecycle gates present in the ledger with monotonic sequence ids and valid hash chain.
- **SC-002**: Test suite passes (>= 47/47 baseline observed) under the Builder run.
- **SC-003**: Builder and Auditor evidence both carry a verifiable ECDSA signature from the registered local identities.
- **SC-004**: Version incremented, commit created, tag created; release notes reference the tag.

## Assumptions
- The operator is the ratifying stakeholder for the freeze exception (per `DS-SELF-GOVERNANCE-001`).
- Hermes execution in this environment is simulated; live enforcement is out of scope for this event.
- Local agent identities in `governance/identities/` + `governance/product-validation/test-keys/` are sufficient for signing evidence.
