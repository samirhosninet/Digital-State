# Tasks: Self-Governance Validation Cycle (DS-SELF-GOVERNANCE-001)

**Input**: Design documents from `governance/self-governance/001-self-governance/`

**Prerequisites**: spec.md (approved), plan.md (Constitution Check PASS).

**Organization**: Tasks grouped by lifecycle gate.

## Format: `[ID] [P?] [Gate] Description`

## Phase 1: Governance Authorization (Prime)
- [x] T001 [P0] Prime issues ALLOW for `DS-SELF-GOVERNANCE-001` and records the freeze-exception rationale in the ledger.
- [x] T002 [P0] Create event workspace `governance/self-governance/001-self-governance/` and seed the ledger with the first hash-chained entry.

## Phase 2: SpecKit Specification (Prime + Builder evidence of spec)
- [x] T003 [SPECIFICATION] Write `spec.md` per SpecKit spec-template; record SPECIFICATION gate in ledger.

## Phase 3: SpecKit Plan
- [x] T004 [PLANNING] Write `plan.md` with Constitution Check (0 violations); record PLANNING gate.

## Phase 4: SpecKit Tasks
- [x] T005 [TASKS] Write `tasks.md` breakdown; record TASKS gate.

## Phase 5: Hermes Kanban Planning (SIMULATED)
- [x] T006 [KANBAN] Create simulated Kanban cards for T007–T009 in `kanban.json`; assign Builder/Auditor; record delegation.

## Phase 6: Builder Execution
- [x] T007 [IMPLEMENTATION] Builder runs real `pytest tests/` (Baseline 47/47+ PASS) and `digitalstate doctor`; emits signed `builder-evidence.json`; record IMPLEMENTATION gate.

## Phase 7: Auditor Independent Verification
- [x] T008 [VERIFICATION] Auditor independently re-runs suite + verifies Builder signature against registered key; emits signed `auditor-verification.json` with veto authority; record VERIFICATION gate.

## Phase 8: Prime Acceptance
- [x] T009 [ACCEPTANCE] Prime signs acceptance record `prime-acceptance.json`; record COMPLETED gate.

## Phase 9: Workspace Update & Release (local)
- [ ] T010 [RELEASE] Increment `pyproject.toml` version; git commit; git tag `v1.5-self-governance`; draft release notes. (GitHub Release prepared as `gh` command — not executed; `gh` CLI absent.)

## Dependencies & Execution Order
- T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 (strictly sequential; each gate blocks the next).

## Notes
- `gh` CLI is NOT installed in this environment; the GitHub Release step is prepared (notes + exact command) but must be run by the operator. This is disclosed, not hidden.
- Hermes execution is simulated; no live Kanban cluster exists. The simulation is recorded faithfully in `kanban.json`.
