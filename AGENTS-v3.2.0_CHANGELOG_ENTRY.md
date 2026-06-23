# CHANGELOG entry for AGENTS.md v3.2.0

## 3.2.0 — 2026-06-20

- Aligned `AGENTS.md` with `skills/digital-state/SKILL.md` v3.2.0 architectural boundaries.
- Added `Framework Scope` to clarify what belongs in `AGENTS.md` versus reusable skills and target-project Spec-Kit files.
- Added `Architecture Invariants` for role separation, evidence-before-judgment, authorization-before-mutation, Kanban-as-ledger, Spec-Kit-as-requirements-layer, companion-skill separation, and no legacy role drift.
- Upgraded Gate Enforcement from three gates to four by adding the `Risk Gate` tied to Premortem Plus.
- Extended handoff format with `Risk Handling` and Builder `Risk Trigger Scan` fields.
- Updated Premortem Plus integration to reference the independent skill without duplicating threshold tables, and to require `Premortem Status` plus canonical `risk-ledger.md` handling when triggered.
- Added `Framework File Hygiene` to keep reusable governance files portable and free from project-specific state.
- Updated references to include Constitution Articles I–X, including Article X on concurrency.

Governance note: per Version Governance, this change should be routed through Builder → Auditor before being treated as in effect.
