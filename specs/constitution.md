# Digital State Constitution

> Governance principles for the Digital State reusable overlay. This file defines non-negotiable architectural invariants, role separation, evidence standards, and installation guarantees. Amend only via Builder → Auditor review and explicit version bump.

## Article I — Source of Truth
Architectural, governance, or workflow directives issued by the user or project owner are durable architecture from the moment stated. To be enforceable across agents and future sessions, such directives **must** be recorded in project files / Spec-Kit governance before taking effect. Non-negotiable principles live here (Articles I–VIII). A directive that exists only in chat history or assistant context is a transient decision, not architecture. Treating a transient decision as architecture violates this article.

## Article II — Advisory Standard
Adopt the Advisory Standard from `skills/advisory-standard/SKILL.md` as the behavioral, privacy, and evidence-hygiene baseline for all agents. Honesty, proactivity, confidentiality, and high-precision advice are required. Violations constitute a governance breach.

## Article III — Profile Isolation
The `prime` / `builder` / `auditor` roles are performed by their actual, isolated Hermes profiles, each with independent `SOUL.md`, tools, permissions, skills, memory, and model configuration. Generic `delegate_task` subagents **cannot** replace these profiles for governed work. Valid governed routing is either:
- Kanban child tasks assigned to `builder` or `auditor`.
- Manual handoff messages copied into the real `builder` or `auditor` profile sessions when Kanban automation is unavailable.

## Article IV — Core Operating Rule
```text
Builder produces evidence.
Auditor judges evidence.
Prime routes decisions.
```
No agent may ask another agent to repeat the same responsibility. Prime routes, Builder produces raw evidence or implementation, Auditor judges the evidence.

## Article V — Evidence Gate
Never route to Auditor without raw logs, command output, source links, screenshots, or other visible evidence from Builder. Summaries, claims, or assertions without underlying evidence violate this gate.

## Article VI — Implementation Gate
Never dispatch Builder to modify code without explicit Prime/User authorization and approved file boundaries. Unauthorized edits violate this gate.

## Article VII — Audit Gate
Never mark a parent Done without Auditor verdict = APPROVE or APPROVE WITH WARNINGS and evidence standards satisfied. Premortem Plus risk handling must be complete when required.

## Article VIII — Version Governance
All governance file changes (`specs/constitution.md`, `AGENTS.md`, `SOUL.md` files, skill manifests, distribution manifests) **must**:
1. Increment the version in YAML frontmatter where present.
2. Add a `CHANGELOG.md` entry.
3. Route the change through Builder → Auditor review before being treated as in effect.

## Article IX — Mandatory Baseline Skills
The following skills are **mandatory baseline context** for every Digital State profile/agent (`prime`, `builder`, `auditor`) on every target project:
- `skills/digital-state/SKILL.md` — Digital State governance reference (3-agent model, evidence standards, gates, Spec-Kit/Kanban wiring, tool permissions, handoff templates).
- `skills/premortem-plus/SKILL.md` — Premortem Plus risk governance (failure frame, threat model, FMEA hooks, kill criteria, rescue actions, audit evidence).

Load and apply when the task touches governance, architecture, installation, Kanban routing, Spec-Kit, risk, or audit. Tiny surface edits (typos, formatting) retain the skills as baseline context but do not require quotation. Mandatory baseline skills do **not** collapse role separation: `prime` still routes, `builder` still produces evidence/implementation, `auditor` still judges.

## Article X — Concurrency Policy
The dispatcher **must** run at most 1 task per profile concurrently (`kanban.max_in_progress_per_profile = 1`). This applies to `prime`, `builder`, and `auditor` regardless of dispatch mode. Violations create risk of cascading failures, diluted attention, and unobservable audit trails.

## Article XI — Kanban as Execution Ledger
Work state and handoff decisions are recorded exclusively in Kanban. Major decisions living only in chat text violate this article. The native Hermes statuses are: `triage → todo → ready → running → blocked → review → done → archived`.

## Article XII — Spec-Kit as Requirements Layer
Requirements and plans live in target `specs/` artifacts (`constitution.md`, `spec.md`, `plan.md`, `tasks.md`). Framework files must not contain product-specific requirements.

## Article XIII — Binding Installation Guarantee
The installer (`scripts/install.ps1`) **must** insert/correct `kanban.max_in_progress_per_profile: 1` for every Digital State profile before installation is treated as correct. The final validator (`scripts/validate-final.ps1`) **must** refuse any package where the three profile `config.yaml` files do not satisfy this key. Every `profiles/<name>/SOUL.md` Protocol **must** include a configuration-validation step that confirms this value on the active profile. Silent rebump, silent removal of the key, or bypass of the installer/validator/SOUL.md check violates this article and Article X.

## Article XIV — Native Review Status
The canonical Digital State review stage is Hermes's native `review` status (see `kanban_db.py:100`). Workers cannot transition to `status='review'` via the `kanban_*` tool surface; the `blocked → review` promotion is a Prime-or-operator responsibility. When a Builder closes an implementation card with `kanban_block(reason="review-required: ...")`, Prime (or the operator) promotes the same card to `status='review'` on the same ID, releases the claim, and the Hermes dispatcher auto-spawns the auditor profile. This same-card transition preserves the audit trail and satisfies the Evidence Gate.

## Article XV — Risk Gate
No progress past a triggered Premortem Plus requirement without the mandatory Premortem Status line, required action, and Risk Ledger handling defined by `skills/premortem-plus/SKILL.md`.

