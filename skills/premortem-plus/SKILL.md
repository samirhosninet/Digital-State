---
name: premortem-plus
description: Premortem Plus risk governance for Digital State — risk scoring, FMEA, threat modeling, deterministic triggers, authoritative mode decision matrix, kill criteria, rescue actions, recurrence escalation, cross-model audit state, and audit evidence for Digital State workflows.
version: 4.3.1
author: Digital State Architecture
metadata:
  changelog:
    - "4.3.1: Synchronized with closure patch; no risk-governance behavioral change beyond v4.3.0."
    - "4.3.0: Final hardening patch — clarified Default Starting Tier as scoring entry only; tied overreach kill criterion to the authoritative Mode Decision Matrix rather than separate numeric thresholds."
    - "4.2.0: Finalized cross-model profile-bound audit metadata; retained DISTINCT/SAME-FAMILY-BY-CHOICE/SAME-FAMILY-UNAVAILABLE/NOT-RECORDED states; removed premature risk_entries table dependency and made Kanban comments/handoffs/run metadata the canonical risk record with risk-ledger.md generated read-only."
    - "4.1.0: Fixed Mode Matrix safety regression by adding FULL-AUDIT-WARN; made Risk Score/RPN bands input classifiers only; replaced binary cross-model OK/NOT AVAILABLE with four explicit launcher-captured states; restored worked examples; aligned human-gate and concurrency assumptions with Digital State v4.1."
    - "4.0.0: Replaced overlapping Mode rules with a single decision matrix. Clarified risk-ledger canonical-store policy for Hermes Kanban/SQLite and read-only generated ledgers. Added cross-model-unavailable recurrence escalation. Aligned confidentiality/evidence rules with Advisory Standard v4 and Digital State v4."
    - "3.1.1: Mandatory status line cleanup and LEDGER-ONLY/MINI separation."
    - "3.1.0: Added LEDGER-ONLY and deterministic trigger tightening."
    - "3.0.0: Mandatory Status Line, default starting tier, cross-model auditing, canonical per-project Risk Ledger."
    - "2.0.0: Bound scores to actions, rubric anchors, deterministic triggers, cross-model auditor requirement."
    - "1.0.0: Initial release."
  hermes:
    tags: [risk, premortem, governance, audit, fmea, threat-modeling, kanban, speckit]
    category: governance
---

# Premortem Plus Risk Governance

Use this skill whenever a Digital State task, Spec-Kit artifact, Kanban card, implementation plan, architecture change, dependency decision, executor choice, model-routing choice, or release could fail in ways that harm correctness, security, reliability, cost, schedule, trust, privacy, or reversibility.

This file owns risk logic. Digital State routes to this skill; Advisory Standard governs conduct, evidence hygiene, and confidentiality.

## Core Idea

```text
Assume the task has already failed.
Identify why.
Turn causes into controls, evidence, kill criteria, rescue actions, and recurrence signals.
Let the computed matrix mode decide the required action.
```

## Agent Responsibilities

| Agent | Responsibility |
|---|---|
| `prime` | Runs prime-discretionary checks, creates/links child cards, enforces gates, escalates user decisions, and records final routing. Cannot suppress deterministic triggers silently. |
| `builder` | Produces raw evidence, command logs, diffs, source links, and mechanical trigger scan results. Does not score final risk or approve. |
| `auditor` | Scores risks against anchors, validates controls, checks threat/FMEA issues, confirms cross-model audit state, and issues exactly one verdict. |

## Trigger Rules

### Deterministic Triggers

These fire mechanically and are not optional:
- File path touches: `auth/`, `payments/`, `migrations/`, `infra/`, `secrets/`, `.env*`, deployment/CI config such as `.github/workflows/`.
- A dependency manifest adds a new external dependency: `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.
- Task title, spec, plan, code, diff, command, or PR text contains: auth, payment, credential, production, migration, delete, drop table, deploy, secret, key rotation.
- Task touches private data, credentials, production systems, destructive operations, or irreversible operations.
- Workflow selection changes the model family assigned to Builder or Auditor.
- Workflow selection changes the external executor used for implementation or audit.

If a deterministic trigger fires, Prime must run the check or escalate a documented exception to the user. Silent suppression is a kill-criterion violation.

### Prime-Discretionary Triggers

Run a check when:
- starting a new project or major feature;
- `spec.md`, `plan.md`, or `tasks.md` changes materially;
- a card is blocked, ambiguous, repeated, looping, or disputed;
- Auditor sees insufficient evidence or high uncertainty;
- recurrence tags may affect the decision.

## Default Starting Tier

This is only an entry heuristic. The decision matrix below is authoritative after scoring.

| Change surface | Default starting mode |
|---|---|
| Copy, UI styling, docs, non-functional text | MINI, then downgrade to LEDGER-ONLY if the matrix permits |
| Business logic, validation, adapter/mapping code, internal API contracts | MINI, promote if score or anchors require |
| Deterministic trigger | FULL minimum |
| Destructive/irreversible/secret/production change | FULL minimum, often ESCALATE |
| Model-family or executor routing change | MINI minimum; promote to FULL if it affects audit independence or execution authority |

> Note: This table only chooses a *starting* point for scoring. The final Mode always comes from the Mode Decision Matrix after the real RPN is computed. A genuine copy/docs change normally yields RPN < 20 (low Severity, immediate Detection), so it stays MINI/LEDGER-ONLY. If a "docs" change somehow scores RPN >= 20, that high score is intentional and FULL is correct.

## Score Definitions

```text
Risk Score = Probability x Impact
Range: 1-25

RPN = Severity x Occurrence x Detection Difficulty
Range: 1-125
```

## Rubric Anchors

### Probability

| Score | Anchor |
|---|---|
| 1 | Theoretical; no precedent in this project or comparable systems |
| 2 | Possible; no precedent here, but known in comparable systems |
| 3 | Has occurred once before in this project |
| 4 | Recurring pattern in this project |
| 5 | Near-certain or already observed this cycle |

### Impact

| Score | Anchor |
|---|---|
| 1 | Cosmetic; no user, data, system, trust, or schedule impact |
| 2 | Degraded experience; fully recoverable; no data loss |
| 3 | Partial functionality loss or recoverable data issue requiring manual fix |
| 4 | Significant data loss, security exposure, trust harm, or extended outage; recoverable with effort |
| 5 | Irreversible or unrecoverable: secret leak, production breach, unbacked data loss, destructive release |

### FMEA

| Score | Severity | Occurrence | Detection Difficulty |
|---|---|---|---|
| 1 | No real consequence | Practically never happens | Existing tests/logs catch immediately |
| 2 | Minor reversible issue | Unlikely | Caught in routine local checks |
| 3 | Manual fix required | Has happened before | Caught during normal review |
| 4 | Serious recoverable failure | Recurring risk | Often missed until integration/release |
| 5 | Irreversible/unrecoverable | Expected to recur without control | Could ship unnoticed |

## Input Classifier Bands

The following bands classify inputs only. They do **not** independently determine the final Mode.

### Risk Score Band

| Risk Score | Input classifier |
|---|---|
| 1-4 | Very low risk |
| 5-9 | Low-to-moderate risk |
| 10-14 | Material risk |
| 15-19 | High risk requiring Auditor review |
| 20-25 | Escalation-class risk |

### RPN Band

| RPN | Input classifier |
|---|---|
| 1-19 | Low FMEA concern |
| 20-39 | Control must be evidenced |
| 40-79 | Warning-ceiling FMEA concern |
| 80-125 | Escalation-class FMEA concern |

## Mode Decision Matrix

This matrix is the **only authoritative source** for the final required Mode.

If any other text appears to conflict with this matrix, this matrix wins.

| Risk Score Band | RPN 1-19 | RPN 20-39 | RPN 40-79 | RPN 80-125 |
|---|---|---|---|---|
| 1-4 | LEDGER-ONLY | FULL | FULL-WARN | ESCALATE |
| 5-9 | MINI | FULL | FULL-WARN | ESCALATE |
| 10-14 | FULL | FULL | FULL-WARN | ESCALATE |
| 15-19 | FULL-AUDIT | FULL-AUDIT | FULL-AUDIT-WARN | ESCALATE |
| 20-25 | ESCALATE | ESCALATE | ESCALATE | ESCALATE |

Mode meanings:
- `LEDGER-ONLY`: record status line and ledger/risk record; no child card required unless recurrence escalates.
- `MINI`: compressed checklist on the existing card.
- `FULL`: full Premortem Plus check and evidence controls.
- `FULL-WARN`: full check; maximum passing verdict is APPROVE WITH WARNINGS; monitoring plan required.
- `FULL-AUDIT`: full check plus mandatory Auditor review before the parent can continue.
- `FULL-AUDIT-WARN`: full check plus mandatory Auditor review; maximum passing verdict is APPROVE WITH WARNINGS; monitoring plan required.
- `ESCALATE`: block and request explicit user/named-owner decision before continuing.

If a deterministic trigger fires, minimum mode is `FULL` even if the numeric matrix would be lower.

## Cross-Model Audit State

Cross-model auditing is not a binary OK/NOT-AVAILABLE flag. The Launcher or workflow runtime must record the selected model and model family for Builder and Auditor before an audit verdict is accepted.

Required fields:

```yaml
builder_model: <model id or name>
builder_model_family: <provider/family>
auditor_model: <model id or name>
auditor_model_family: <provider/family>
cross_model_audit_state: DISTINCT | SAME-FAMILY-BY-CHOICE | SAME-FAMILY-UNAVAILABLE | NOT-RECORDED
cross_model_reason: <required unless DISTINCT>
```

State definitions:

| State | Meaning | Verdict effect | Required action |
|---|---|---|---|
| `DISTINCT` | Builder and Auditor use different model families | Clean APPROVE is possible if all other criteria pass | Record state in status line |
| `SAME-FAMILY-BY-CHOICE` | A distinct family is available, but same-family audit was selected | For qualifying items, maximum passing verdict is APPROVE WITH WARNINGS | Warn user/Prime that rerunning Auditor with a distinct family would remove the cap |
| `SAME-FAMILY-UNAVAILABLE` | No distinct auditor family is available in the current deployment | For qualifying items, maximum passing verdict is APPROVE WITH WARNINGS | Add recurrence tag `cross-model-unavailable` |
| `NOT-RECORDED` | Model family metadata is missing | Audit evidence is incomplete | REJECT until metadata is recorded |

A qualifying item is any item with Risk Score >= 10 or RPN >= 20.

`cross-model-unavailable` escalates after 3 occurrences in the same project. `SAME-FAMILY-BY-CHOICE` does not count as unavailable; it is a selectable operational weakness and should normally be fixed by rerunning Auditor with a distinct family when available.

## Mandatory Status Line

Every check must open its Kanban comment with:

```text
Premortem Status
Mode: LEDGER-ONLY / MINI / FULL / FULL-WARN / FULL-AUDIT / FULL-AUDIT-WARN / ESCALATE
Trigger: deterministic / prime-discretionary
Risk Score: <n>
RPN: <n>
Required Action: <from matrix>
Can parent card continue: YES / NO
Evidence required before Done: <bullet list or "none">
Recurrence Tag: <tag or "none">
Builder model/family: <model> / <family>
Auditor model/family: <model> / <family>
Cross-model auditor: DISTINCT / SAME-FAMILY-BY-CHOICE / SAME-FAMILY-UNAVAILABLE / NOT-RECORDED — reason: <short reason>
```

A check without this header is incomplete.

## Threat Model Prompts

Use STRIDE prompts:
- Spoofing: Can identity, profile, or role be impersonated?
- Tampering: Can files, config, data, or evidence be altered without detection?
- Repudiation: Can decisions be reconstructed from the audit trail?
- Information Disclosure: Can secrets, prompts, logs, private data, or credentials leak?
- Denial of Service: Can loops, locks, dependencies, or tool failures halt work?
- Privilege Escalation: Can an agent bypass role, file, tool, or authorization boundaries?

## Kanban Integration

- Prime creates/links child risk-check cards when matrix mode requires them.
- Builder gathers raw evidence and mechanical trigger scan.
- Auditor scores, validates controls, records cross-model audit state, and posts verdict.
- Prime records the final routing decision on the parent card.
- Kill criteria block the parent card immediately.


## Spec-Kit Integration
- Premortem Plus uses Spec-Kit artifacts (spec.md, plan.md, tasks.md) to identify risk surfaces.
- Changes to spec.md, plan.md, or tasks.md trigger prime-discretionary risk checks.
- The risk assessment should consider the requirements and plans in Spec-Kit.


## Spec-Kit Integration
- Premortem Plus uses Spec-Kit artifacts (spec.md, plan.md, tasks.md) to identify risk surfaces.
- Changes to spec.md, plan.md, or tasks.md trigger prime-discretionary risk checks.
- The risk assessment should consider the requirements and plans in Spec-Kit.

## Risk Ledger Policy

### Canonical Store

For Digital State, the canonical risk record is the Hermes Kanban execution ledger:

1. Kanban card comments and handoffs;
2. parent-child links;
3. run metadata JSON where the active Hermes tool/API supports metadata;
4. audit verdict comments containing the Mandatory Status Line.

Do not require a custom `risk_entries` table for the baseline workflow. A structured DB table may be added later by project ADR, but it is not a prerequisite for safe operation.

`risk-ledger.md` is a generated, read-only report produced from the canonical Kanban/runs record. It is not a live multi-writer store.

### Compatibility Fallback

If the project does not yet have DB-backed Kanban/runs metadata available:
- Prime is the only role allowed to write `risk-ledger.md`.
- Builder and Auditor write risk evidence to Kanban cards or approved handoff comments.
- Prime serializes those entries into the markdown ledger.
- No two agents may write `risk-ledger.md` directly.

Risk record fields:

| Date | Project | Card ID | Mode | Risk Score | RPN | Verdict | Recurrence Tag | Cross-model State | Resolution |
|---|---|---|---|---:|---:|---|---|---|---|

## Recurrence Rules

If a recurrence tag appears 3+ times in the same project, escalate one matrix tier unless already ESCALATE.

Standard tags:
- `dependency-risk`
- `secret-exposure`
- `evidence-gap`
- `overreach`
- `cross-model-unavailable`
- `boundary-breach`
- `deterministic-trigger-suppressed`

## Minimal Output for Small Tasks

For `LEDGER-ONLY`, record only the Mandatory Status Line plus the risk record.

For `MINI`, use:

```text
Premortem Plus Mini-Check
- Likely failure:
- Probability x Impact = Risk Score:
- RPN:
- Matrix Mode:
- Hidden assumption:
- Required evidence:
- Kill criterion:
- Rescue action:
- Cross-model audit state:
- Verdict:
```

## Full Template

```text
## Premortem Plus Check

### 1. Failure Frame
- Failed outcome:
- Stakeholders harmed:
- Most visible symptom:
- Irreversible damage, if any:

### 2. Assumptions
| ID | Assumption | Evidence Needed | Owner | Status |
|---|---|---|---|---|

### 3. Failure Scenarios
| ID | Scenario | Probability | Impact | Risk Score | Matrix Mode | Early Warning Signal | Preventive Control | Owner |
|---|---|---:|---:|---:|---|---|---|---|

### 4. FMEA Hooks
| Component / Step | Failure Mode | Effect | Cause | Detection | Severity | Occurrence | Detection Difficulty | RPN | Matrix Mode | Control |
|---|---|---|---|---|---:|---:|---:|---:|---|---|

### 5. Threat Model
Answer STRIDE prompts.

### 6. Evidence Requirements
- Raw logs required:
- Source links required:
- Diffs/screenshots required:
- Test/build/lint output required:
- Acceptance criteria requiring special proof:
- Builder model/family:
- Auditor model/family:
- Cross-model audit state:

### 7. Kill Criteria
Stop or block immediately if any criterion below applies.

### 8. Rescue Actions
| Trigger | Immediate Action | Owner | Recovery Evidence |
|---|---|---|---|

### 9. Auditor Verdict
Pick exactly one verdict with rationale.
```

## Kill Criteria

Block immediately if:
- credentials, tokens, private data, or secrets appear in evidence or logs;
- implementation exceeds approved file boundaries;
- required evidence is missing, summarized, or unverifiable;
- a migration, deletion, deployment, or irreversible action lacks explicit authorization;
- a repeated loop occurs without new evidence or new decision;
- Auditor cannot map evidence to acceptance criteria;
- deterministic trigger was suppressed without logged user-approved exception;
- RPN >= 80 without recorded user risk acceptance;
- `cross_model_audit_state` is `NOT-RECORDED` on any audit;
- A Mode higher than the Mode Decision Matrix requires was run on a prime-discretionary item without documented ambiguity justification. This is `overreach`. Example: running FULL when the matrix returns MINI or LEDGER-ONLY.

## Verdict Definitions

**APPROVE** — All evidence requirements met with raw evidence. No kill criteria triggered. Matrix Mode permits clean approval. Cross-model state is `DISTINCT` or the item is not qualifying for cross-model cap.

**APPROVE WITH WARNINGS** — Evidence requirements met, but at least one applies: Mode is `FULL-WARN` or `FULL-AUDIT-WARN`; Risk Score 15-19; RPN 40-79; qualifying item uses `SAME-FAMILY-BY-CHOICE` or `SAME-FAMILY-UNAVAILABLE`; a non-blocking control is deferred with named owner and deadline. Must include monitoring plan.

**REJECT** — Any kill criterion triggered, evidence is missing/summarized where raw evidence was required, or cross-model state is `NOT-RECORDED`.

**ESCALATE** — Mode is `ESCALATE`; Risk Score >= 20; RPN >= 80; ambiguity cannot be resolved from evidence; or unresolved suppression/residual-risk decision needs user adjudication.

## Worked Examples

| Action | Deterministic trigger? | Likely starting mode | Why |
|---|---|---|---|
| Add a new external dependency | Yes | FULL minimum | Supply-chain risk; mechanical trigger fires |
| Change adapter/mapping logic | No | MINI, re-score | Promote if contract behavior or downstream compatibility changes |
| Run a database migration | Yes | FULL or ESCALATE | Irreversible-class operation |
| Delete or restructure orchestrator files | Yes | FULL or ESCALATE | High blast radius and rollback complexity |
| Change model routing config | Yes for audit governance | MINI/FULL depending scope | Cross-model audit state may change |
| Builder and Auditor same family although distinct family is available | No deterministic code trigger, but governance warning | FULL-WARN on qualifying items | `SAME-FAMILY-BY-CHOICE`; rerun Auditor with distinct family if clean APPROVE is needed |
| No distinct auditor model exists in deployment | No deterministic code trigger, but governance warning | FULL-WARN on qualifying items | `SAME-FAMILY-UNAVAILABLE`; recurrence tag after each occurrence |
| UI copy-only change | No | MINI, maybe LEDGER-ONLY | Downgrade if matrix permits and no uncertainty remains |
| Publish technical/legal/medical/financial claim | Possibly | FULL if high-stakes | Fact/trust risk, brand/reliability harm |

## References

- `skills/digital-state/SKILL.md` — routing, launcher, gates, executor boundaries.
- `skills/advisory-standard/SKILL.md` — conduct, evidence hygiene, confidentiality boundary.
- Target project specs and Kanban cards — project-specific facts.
