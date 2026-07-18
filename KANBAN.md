# Digital State Kanban Board

## Backlog
- [ ] Implement multi-tenant key server authentication
- [ ] **DEFECT (DS-END-TO-END-INSTALL-VALIDATION-001): Runtime does not LOAD Constitution/Architecture/Profiles** — `governance/self-governance/runtime.py` assumes the repo tree exists but never parses/validates `governance/CONSTITUTION_v1.md`, `specs/ARCHITECTURE.md`, or `src/.../profiles/*`. Phase-3 bootstrap validation fails the "system loads these without manual intervention" criterion. Fix: add a `load_governance_context()` step in runtime.py that reads + asserts those paths exist and parses minimal headers, recorded in the ledger as `GOVERNANCE_LOAD`. No new roles/layers.
- [ ] **DEFECT (DS-END-TO-END-INSTALL-VALIDATION-001): runtime.py is hardcoded to a single event** — `EVENT_ID = "DS-RUNTIME-WORKFLOW-INTEGRATION-001"`; there is no generic "start a new project from zero" entrypoint for a real new user. Phase-4 "new project from scratch, generic sequence" is not satisfied by a fixed-card runtime. Fix: parametrize `EVENT_ID`/feature name via CLI args so `runtime.py --new <feature>` drives the full sequence for an arbitrary project. No new roles/layers.

## In Progress
- [/] Native Hermes runtime integration (`feat-003`) - Linked to [spec.md](file:///D:/Digital-State/specs/003-hermes-runtime-integration/spec.md)

## Completed
- [x] Initial Governance Kernel bootstrap (`feat-001`)
