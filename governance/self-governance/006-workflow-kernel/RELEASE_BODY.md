## Digital State v1.8 — Workflow Engine Codified (`v1.8-workflow-kernel`)

**Version:** `1.8.0` | **Prior:** `1.7.0` | **Event:** `DS-WORKFLOW-KERNEL-001`
**Date:** 2026-07-18 | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified, FINAL GOVERNANCE DIRECTIVE)
**Repo:** `samirhosninet/Digital-State`

> Governance-process release. Codifies the *existing* constitutional governance cycle as a **Workflow Engine (state machine)** — the single authority over lifecycle transitions — and codifies the **GitHub Release Workflow** so a new version is published automatically *after* Human Approval (no chat-driven coordination). No constitution/architecture/source-product change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `1.7.0 -> 1.8.0`** only (pyproject.toml). No runtime/API change.
- Added Workflow Engine artifacts under `governance/self-governance/`:
  - `_engine/workflow_kernel.py` — the authoritative state machine (12 states). The ONLY source of truth for transitions.
  - `002-bootstrap/kanban_orchestrator.py` (upgraded) — routes every card move through the kernel; chat is input-only.
  - `006-workflow-kernel/engine_selftest.py` — proves the engine enforces the cycle (9 illegal transitions denied).
  - `006-workflow-kernel/ds_workflow_kernel_event.py` — runs the cycle and, after Human Approval, the Release Workflow.

## What it proves (vs. v1.7)
| Proof | Result |
|-------|--------|
| Governance lifecycle runs on itself | ✅ (v1.5) |
| Runnable Hermes-compatible Kanban Orchestrator | ✅ (v1.6) |
| Operational cycle end-to-end | ✅ (v1.6-opval) |
| Agent role boundaries enforced | ✅ (v1.7) |
| **Workflow codified as state machine; transitions solely kernel-enforced** | ✅ (v1.8) |
| **Release Workflow automated after Human Approval (no manual chat coordination)** | ✅ (v1.8) |
| Ledger integrity (hash-chained, signed) | ✅ valid across all events |
| Auditor independent verification | ✅ no self-approval |

## How users run a new project this way
1. User talks to Prime only. 2. Prime creates Spec (SpecKit) + Kanban card (kernel-enforced).
3. Builder picks its card; executes + evidence. 4. Auditor picks verification card; PASS/FAIL.
5. Prime reviews. 6. **Human approves.** 7. System auto-commits, bumps, tags, publishes Release.
No step depends on manually messaging an agent — only the intended human approval.

```bash
uv run --no-sync python governance/self-governance/006-workflow-kernel/engine_selftest.py
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py --reset
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py
# after human approval:
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py --finalize=VERIFIED
```

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator is faithfully labeled.
- Known finding (Auditor, carried): `integrations/hermes/README.md` claims `LIVE` while `hermes` CLI is absent (spec 009 US2). This release uses simulated Kanban.
