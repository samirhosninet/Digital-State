## Digital State v1.7 — Role Boundary Verified (`v1.7-role-boundary`)

**Version:** `1.7.0` | **Prior:** `1.6.0` | **Event:** `DS-RELEASE-PUBLICATION-001`
**Date:** 2026-07-18 | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified)
**Repo:** `samirhosninet/Digital-State`

> Governance-process release. Proves the Digital State is an **operational governance system** with **testable authority boundaries** — not just a task orchestrator. No constitution/architecture/source-product change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `1.6.0 -> 1.7.0`** only (pyproject.toml). No runtime/API change.
- Added self-application governance evidence under `governance/self-governance/`:
  - `003-operational-validation/` — full operational run (Governance→Planning→Execution→Independent Verification→Human Acceptance).
  - `004-role-boundary/` — 3 agent-boundary tests, all DENY as constitution requires.
  - `005-release-publication/` — this release record.

## What was proven?
| Proof | Result |
|-------|--------|
| Governance lifecycle runs on itself | ✅ (DS-SELF-GOVERNANCE-001, v1.5) |
| Runnable Hermes-compatible Kanban Orchestrator | ✅ (DS-BOOTSTRAP-REAL-WORLD-001, v1.6) |
| Operational cycle end-to-end | ✅ (DS-FIRST-OPERATIONAL-VALIDATION-001) |
| Agent role boundaries enforced | ✅ Prime/Builder/Auditor each DENY out-of-scope requests |
| Ledger integrity (hash-chained, signed) | ✅ valid across all events |
| Auditor independent verification | ✅ no self-approval |

## How do users update?
No runtime/API migration needed. To reproduce any self-application event:
```bash
uv run --no-sync python governance/self-governance/004-role-boundary/role_boundary_harness.py --reset
uv run --no-sync python governance/self-governance/004-role-boundary/role_boundary_harness.py
# then: ...role_boundary_harness.py --finalize=VERIFIED
```

## Evidence summary (release completeness — all 5 aligned)
- **Code:** present, no product change.
- **Tests:** `pytest` green (58 tests, 100%) at release commit.
- **Ledger:** all event ledgers `valid: True` (hash-chained, ECDSA-signed).
- **Governance Evidence:** SpecKit artifacts + signed Builder/Auditor/Prime records per event.
- **Public Release:** this GitHub Release, linked to tag `v1.7-role-boundary`.

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator is faithfully labeled.
- Known finding (Auditor): `integrations/hermes/README.md` + `doctor` claim `connection_type: "LIVE"` while `hermes` CLI is absent and the top README says mock (spec 009 US2). This release uses simulated Kanban.
