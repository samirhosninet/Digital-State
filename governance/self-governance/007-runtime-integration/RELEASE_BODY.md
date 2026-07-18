## Digital State v1.9 — Runtime Workflow Integration (`v1.9-runtime-integration`)

**Version:** `1.9.0` | **Prior:** `1.8.0` | **Event:** `DS-RUNTIME-WORKFLOW-INTEGRATION-001`
**Date:** 2026-07-18 | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified)
**Repo:** `samirhosninet/Digital-State`

> Makes the codified constitutional workflow the **repository runtime workflow** a clean local install can execute **without chat coordination**. The runtime itself coordinates Prime→Builder→Auditor→Prime→Human→Release through the Hermes Kanban Orchestrator (operational coordinator) driven by the Workflow Kernel (sole transition authority). No constitution/architecture/source change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `1.8.0 -> 1.9.0`** only (pyproject.toml).
- Added `governance/self-governance/runtime.py` — single reproducible entrypoint. A clean
  `git clone` + `uv sync` + `uv run python governance/self-governance/runtime.py --demo` reproduces
  the full lifecycle (spec/plan/tasks → Kanban → Builder → Auditor → Human gate).
- Generated SpecKit artifacts come from the repo's own `.specify/templates/` (no external `specify` binary).

## Reproducible on a clean install
```bash
git clone samirhosninet/Digital-State && cd Digital-State
uv sync                      # installs digitalstate + deps
uv run python governance/self-governance/runtime.py --demo     # full cycle, halts at Human gate
# after human approval:
uv run python governance/self-governance/runtime.py --finalize=VERIFIED
```
| Proof | Result |
|-------|--------|
| Runtime workflow starts automatically (entrypoint) | ✅ |
| Prime creates SpecKit artifacts (spec/plan/tasks) | ✅ (from repo templates) |
| Hermes Kanban populated automatically | ✅ (orchestrator-driven) |
| Builder receives work through Kanban | ✅ |
| Auditor receives verification through Kanban | ✅ |
| Human Approval gate mandatory | ✅ (kernel forbids agent crossing) |
| GitHub repo updated automatically after approval | ✅ (commit/tag/push) |
| GitHub Release published + version public | ✅ |
| Governance Ledger records lifecycle | ✅ (all transitions) |

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator faithfully labeled.
- Known Auditor finding carried: `integrations/hermes/README.md` claims `LIVE` while `hermes` CLI is absent (spec 009 US2).
