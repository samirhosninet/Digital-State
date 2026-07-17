# Release Notes — Digital State Self-Governance Event `DS-SELF-GOVERNANCE-001`

**Event Tag:** `v1.5-self-governance`
**Release Commit:** (created by this event — see `git show v1.5-self-governance`)
**Date:** 2026-07-18
**Authority:** Prime (operator-ratified limited exception to the READ-ONLY Product Validation freeze)

> This is a **governance-process release**, not a product/feature release. It proves the Digital State lifecycle can run on itself. The frozen product baseline (`specs/`, `src/`, `framework/`, `integrations/`, `release/`, `DS-CONSTITUTION-001`, `DS-ARCHITECTURE-001`) is **unchanged**. All artifacts live under `governance/self-governance/001-self-governance/`.

## What changed
- Added the self-governance event package: `spec.md`, `plan.md`, `tasks.md`, hash-chained `ledger.jsonl`, simulated `kanban.json`, signed `builder-evidence.json`, signed `auditor-verification.json`, `prime-acceptance.json`, and the reproducible `build_event.py` harness.
- Bumped package version `0.1.0 → 1.5.0` to make the Workspace Update a real, traceable increment tied to tag `v1.5-self-governance`.

## Lifecycle gates (all 8 entries hash-chained, chain verifies VALID)
1. `GOVERNANCE_EVENT` — Prime ALLOW + freeze-exception rationale
2. `SPECIFICATION` — approved (`spec.md`)
3. `PLANNING` — approved (`plan.md`, Constitution Check: 0 violations)
4. `TASKS` — approved (`tasks.md`)
5. `DELEGATION` — simulated Hermes Kanban: K001→builder, K002→auditor
6. `IMPLEMENTATION` — Builder evidence (signed): test suite green, `doctor` overall PASS
7. `VERIFICATION` — Auditor independent pass (signed, `veto: false`)
8. `COMPLETED` — Prime signed acceptance

## Evidence
- **Builder**: real `pytest` run returned exit 0; `digitalstate doctor` overall_status PASS. Evidence signed with `builder-agent` key, signature verified by Auditor.
- **Auditor**: independent `pytest` re-run returned exit 0; Builder signature verified valid. Auditor signed with `auditor-agent` key (independent of Builder — no self-approval).

## Findings surfaced by the independent Auditor (recorded honestly)
1. **Hermes runtime-claim inconsistency**: `integrations/hermes/README.md` and `digitalstate doctor` report `connection_type: "LIVE"`, but the `hermes` CLI binary is **not installed** in this environment and the top-level `README.md` states the Hermes layer is a **mock/simulation** boundary. This is exactly the false-live-runtime risk `spec 009 US2` was built to prevent. This event therefore uses a **simulated Kanban** and asserts **no live enforcement**.
2. **Version-source inconsistency**: `pyproject.toml` was `0.1.0` while git release tags run to `v1.4-release`. This event reconciles the event line to `1.5.0` / `v1.5-self-governance`. Recommend a follow-up governance event to make the package version track the release tags consistently.

## Environment limits (disclosed, not hidden)
- **No `gh` CLI** in this environment → the GitHub Release step is prepared below but **not executed**. Run it as the operator.
- **Hermes is simulated** → "Hermes Kanban Planning" and "Builder/Auditor via Hermes" are faithfully-recorded simulations, not a live execution cluster.

## GitHub Release command (run as operator)
```bash
gh release create v1.5-self-governance \
  --title "Digital State Self-Governance Event DS-SELF-GOVERNANCE-001" \
  --notes-file governance/self-governance/001-self-governance/RELEASE_NOTES.md \
  --repo samirhosninet/Digital-State
```

## Test Success
- Baseline suite: 100% pass (57–58 tests observed across runs; `pytest` exit 0).
