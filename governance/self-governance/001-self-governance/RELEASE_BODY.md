## Digital State Self-Governance Event — `DS-SELF-GOVERNANCE-001`

**Version:** `v1.5-self-governance`
**Release tag:** `v1.5-self-governance` → commit `dbcb0f1`
**Date:** 2026-07-18
**Authority:** Prime (operator-ratified limited exception to the READ-ONLY Product Validation freeze)

> This is a **governance-process release**, not a product/feature release. It proves the Digital State lifecycle can run on itself. The frozen product baseline (`specs/`, `src/`, `framework/`, `integrations/`, `release/`, `DS-CONSTITUTION-001`, `DS-ARCHITECTURE-001`) is **unchanged**. All artifacts live under `governance/self-governance/001-self-governance/`.

## Evidence summary
- **SpecKit artifacts:** `spec.md`, `plan.md`, `tasks.md` (plan includes a Constitution Check gate: **0 violations**).
- **Hash-chained ledger:** `ledger.jsonl` — 8 sequentially numbered, hash-chained entries; chain verified VALID.
- **Builder evidence (signed):** real `pytest` run returned exit 0 (58 tests, 100% pass); `digitalstate doctor` overall_status PASS. Signed with `builder-agent` key; signature verified by Auditor.
- **Auditor verification (signed, independent):** independent `pytest` re-run returned exit 0; Builder signature verified valid. Auditor signed with `auditor-agent` key — no self-approval, veto authority retained (`veto: false`).
- **Prime acceptance (signed):** recorded gate `COMPLETED`.

## Architectural impact
- **None.** No changes to `DS-ARCHITECTURE-001`, no new layers, no new roles, no authority-model change. The event is confined to `governance/self-governance/`. The only source touch is a version-string bump in `pyproject.toml` (`0.1.0 → 1.5.0`) to make the Workspace Update a traceable increment.

## Migration / update instructions
This release introduces no runtime/API changes, so **no migration is required** for existing installs. For reproducibility of the governance evidence:
```bash
# Regenerate the full evidence package locally (auditor-verifiable):
uv run --no-sync python governance/self-governance/001-self-governance/build_event.py --reset

# Inspect the immutable ledger:
cat governance/self-governance/001-self-governance/ledger.jsonl
```

## Honest environment limitations (disclosed)
- **Hermes execution is simulated** in this environment (no live Hermes cluster, no live Kanban tools). "Hermes Kanban Planning" and "Builder/Auditor via Hermes" are faithfully-recorded simulations; no live enforcement is asserted.
- **Auditor finding (recorded):** `integrations/hermes/README.md` and `digitalstate doctor` report `connection_type: "LIVE"`, but the `hermes` CLI binary is not installed and the top-level README states the Hermes layer is a **mock/simulation** boundary. This is the false-live-runtime risk `spec 009 US2` was built to prevent.
- **Version-source inconsistency (recorded):** `pyproject.toml` was `0.1.0` while release tags ran to `v1.3-release`; reconciled to `1.5.0` for this event line. A follow-up governance event should make the package version track release tags consistently.
