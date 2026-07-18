## Digital State Bootstrap — `DS-BOOTSTRAP-REAL-WORLD-001`

**Version:** `v1.6-bootstrap` | **Commit:** (tag deref) | **Date:** 2026-07-17
**Authority:** Prime (operator-ratified limited exception to READ-ONLY freeze)

> Governance-process release. Turns the Digital State lifecycle into a *runnable* system in-workspace via a Hermes-compatible Kanban Orchestrator (`governance/self-governance/002-bootstrap/kanban_orchestrator.py`). No constitution/architecture/source-product change, no new roles/layers.

## Evidence summary
- **Runnable orchestrator:** `kanban_orchestrator.py` creates/assigns/transitions cards; each transition is mirrored to the hash-chained `ledger.jsonl` (chain verified VALID).
- **SpecKit artifacts:** `spec.md`, `plan.md`, `tasks.md` (Constitution Check: 0 violations).
- **Builder evidence (signed):** real `pytest` run green (58 tests, 100%); `digitalstate doctor` overall PASS.
- **Auditor verification (signed, independent):** independent `pytest` re-run green; Builder signature verified; `veto: false`.
- **Prime acceptance (signed):** gate `COMPLETED`.

## Architectural impact
**None.** `Digital State = Governance`, `Hermes = Execution (simulated locally)`, `Adapter = Bridge`, `Agents = Roles` preserved. Only `pyproject.toml` version bumped `1.5.0 -> 1.6.0`.

## Migration / update
No runtime/API change; no migration needed. Reproduce:
```bash
uv run --no-sync python governance/self-governance/002-bootstrap/run_bootstrap.py
```

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). The orchestrator is faithfully-labeled; no live enforcement asserted.
- Auditor finding (recorded): `integrations/hermes/README.md` + `doctor` claim `connection_type: "LIVE"` while the `hermes` CLI is absent and the top README says mock — the false-live-runtime risk `spec 009 US2` targets. This event uses simulated Kanban.
