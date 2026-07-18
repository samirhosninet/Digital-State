# DS-END-TO-END-INSTALL-VALIDATION-001 — Clean Install Validation Report

**Authority:** Human Prime (Final Authority), operator-ratified validation exception.
**Date:** 2026-07-18 · **Repo:** `samirhosninet/Digital-State` · **Branch validated:** `main` (default new-user clone)
**Harness:** `007-runtime-integration/acceptance_harness.py --branch=main` (real GitHub clone)

---

## Phase 1 — Repository Publication Verification ✅ PASS

| Check | Result |
|---|---|
| Latest commit on `origin` | ✅ HEAD `7e42b21` = `origin/spec-012/authority-remediation` = `origin/main` (PR #3 merged). Unpushed local commits: **none**. |
| Latest tag published | ✅ `v1.9-runtime-integration` → remote `407dabc…` (annotated), points to `e842581` release commit. |
| Latest GitHub Release published | ✅ [v1.9-runtime-integration](https://github.com/samirhosninet/Digital-State/releases/tag/v1.9-runtime-integration) |
| Unpushed commits? | ✅ none — every change is on GitHub. |

**Note (corrected earlier assumption):** the v1.9 tag points to `e842581` (the runtime/runtime-workflow commit), while HEAD is `7e42b21` (the acceptance evidence commit). Both are on `main`. The release covers the v1.9 code; the evidence commit is a post-release documentation commit — acceptable, but **recommend** re-tagging v1.9 at HEAD for tidy traceability.

---

## Phase 2 — Clean Installation ✅ PASS

- New empty temp workspace; `git clone --branch=main` from GitHub → `rc=0`.
- `uv sync` in the clone → `rc=0` (Digital State installed, no host files used).
- **No files/settings from the dev environment were reused** (ephemeral temp dir, fresh `uv sync`).

---

## Phase 3 — Bootstrap Validation ⚠️ PARTIAL (DEFECT recorded)

The required artifacts exist in the cloned tree **and are reachable**, but the **runtime does not load/parse them**：

| Artifact | Present in clone | Loaded by `runtime.py` |
|---|---|---|
| Constitution (`governance/CONSTITUTION_v1.md`) | ✅ | ❌ not parsed |
| Architecture (`specs/ARCHITECTURE.md`) | ✅ | ❌ not parsed |
| Profiles (`src/.../profiles/*`) | ✅ | ❌ not parsed |
| Runtime entrypoint (`runtime.py`) | ✅ | ✅ (self) |
| Workflow Kernel (`_engine/workflow_kernel.py`) | ✅ | ✅ imported |
| Hermes Integration (Orchestrator) | ✅ | ✅ imported (simulated) |

**→ DEFECT CARD (Backlog):** Runtime must `load_governance_context()` and assert/parse these without manual intervention. Repo facts: Constitution + Architecture + Profiles are **all published on `main`** — the gap is runtime *validation*, not availability.

---

## Phase 4 — Real Workflow Validation ✅ PASS (sequence + no-chat) ⚠️ event-coupled

Clean clone ran `runtime.py` end-to-end, **zero chat coordination**:
```
GOVERNANCE_EVENT(Prime ALLOW) → SPECKIT(spec/plan/tasks) → KANBAN card K001
 → PRIME_SPECKIT → KANBAN_CREATED → BUILDER_QUEUE → BUILDER_EXECUTION(builder-agent)
 → READY_FOR_AUDIT → AUDITOR_REVIEW(auditor-agent) → READY_FOR_PRIME
 → PRIME_REVIEW → HUMAN_APPROVAL(prime-agent may ENTER, kernel forbids EXIT)
```
- No stage skipped/merged; kernel `can_advance` is sole authority; 9 illegal transitions denied.
- Halted at **mandatory `HUMAN_APPROVAL`** gate (agent cannot cross). ✅

**⚠️ DEFECT (event coupling):** `runtime.py` hardcodes `EVENT_ID="DS-RUNTIME-WORKFLOW-INTEGRATION-001"` and a fixed feature. A real new user "starting a project from zero" has **no generic entrypoint** — Phase 4's generic new-project sequence is not satisfied by a single fixed-card runtime.
**→ DEFECT CARD (Backlog):** parametrize `runtime.py --new <feature>` to drive the full sequence for an arbitrary project. No new roles/layers.

---

## Phase 5 — GitHub Publication Validation ✅ PASS (post Human Approval)

Authorized by this card (Human Approval surrogate) → Release Workflow executed:
- Version bump `1.8.0 → 1.9.0` ✅
- Git commit + Tag `v1.9-runtime-integration` ✅
- GitHub push ✅ · GitHub Release published ✅
- Governance Ledger appended + `valid: True` ✅
- Result visible to any other user via the GitHub Release URL above. ✅

---

## Defects found (must be fixed before "production-ready")

| ID | Defect | Severity | Kanban |
|---|---|---|---|
| D1 | Runtime does not load/validate Constitution/Architecture/Profiles | Medium | Backlog card |
| D2 | `runtime.py` hardcoded to one event; no generic new-project entrypoint | Medium | Backlog card |

No step in the validated path depends on **chat-message coordination** — the workflow runs entirely inside the Runtime (kernel + orchestrator). The two defects are *completeness gaps*, not chat-dependencies.

---

## Prime Verdict

**REPRODUCIBLE FROM A CLEAN GITHUB CLONE: YES** — a new user on `main` can `git clone` + `uv sync` + `uv run python governance/self-governance/runtime.py` and watch the full governance lifecycle run with **no chat**, halting at the Human gate, then auto-release after approval.

**PRODUCTION-READY: NO** (per card rule) — until D1 + D2 are fixed. The workflow is genuinely in the Runtime, but (a) it doesn't validate the governance documents it ships, and (b) it isn't yet a generic new-project entrypoint.

**Constitutional status:** no new Roles/Layers; no constitution/architecture/`src` change; Human Final Authority preserved; Digital State = Governance Plane, Hermes = simulated Execution Kernel.
