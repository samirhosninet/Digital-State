---
name: digital-state
description: Digital State governance reference — standalone architecture skill for Hermes Desktop Digital State Launcher, Prime/Builder/Auditor operating model, evidence gates, Kanban routing, Spec-Kit boundaries, tool permissions, executor integration, model-family capture, handoff contracts, and companion-skill integration.
version: 3.2.0
author: Digital State Architecture
metadata:
  changelog:
    - "4.3.1: Closure patch — replaced duplicate fallback completion wording with a canonical sequence plus cross-reference to reduce maintenance drift."
    - "4.3.0: Final hardening patch — added explicit fallback completion sequence for Auditor-child review fallback; added precedence rules for governance conflicts; retained liveness-only heartbeat semantics."
    - "4.2.0: Finalized Hermes status mapping against current source: triage/todo/scheduled/ready/running/blocked/review/done/archived. Added review-state fallback because first-class request-review is not yet exposed in normal CLI/tool flows. Clarified that CAS/WAL/claim/heartbeat are native Hermes kernel responsibilities and must not be reimplemented by Digital State."
    - "4.1.0: Added launcher-captured model-family metadata and derived cross-model audit state; made Human Decision Gate enforceable through blocked status; marked multi-builder concurrency policy inactive until ADR enables it; replaced auditor-readonly ambiguity with auditor-verification-safe allowlist; aligned with Premortem Plus v4.1."
    - "4.0.0: Redesigned for Hermes Desktop Digital State Launcher: Project -> Agent -> Model -> Toolset -> Workflow -> Executor -> Start. Added external executor boundaries for Codex/Claude/GitHub/MCP, clarified kanban_complete child-only semantics, risk ledger policy, and SQLite concurrency baseline."
    - "3.2.0: Standalone Digital State skill; companion-skill boundaries; architecture invariants; Premortem Plus integration."
    - "3.1.0: Existing 3-agent governance reference."
  hermes:
    tags: [governance, multi-agent, kanban, architecture, launcher, workflow]
    category: workflow
---

# Digital State Governance Reference

Load this skill when you need the full governance context beyond project `AGENTS.md`.

Digital State is a reusable governance overlay for any target project. Hermes Desktop is the intended control surface. Spec-Kit provides requirements and planning artifacts. Hermes Kanban provides task state, evidence, approvals, and audit trail. Premortem Plus is an independent companion skill for risk logic. Advisory Standard is an independent companion skill for conduct and evidence hygiene.

## Core Rule

```text
Builder produces evidence.
Auditor judges evidence.
Prime routes decisions.
```

No agent should ask another agent to repeat the same responsibility. Builder produces raw evidence or implementation, Auditor judges it, and Prime routes the decision.

## Hermes Desktop Digital State Launcher

The Launcher is a selection layer, not a new agent runtime.

It should let the user choose:

```text
Project -> Agent -> Model -> Toolset -> Workflow -> Executor -> Start
```

The Launcher must translate those choices into a bounded Hermes session with explicit metadata, allowed tools, workflow prompt, and stop condition.

### Required Launcher Fields

```yaml
project:
  id:
  path:
  kanban_board:
  specs_path:
  constitution_path:
  agents_file:

session:
  agent_role: prime | builder | auditor | specialist
  model:
  model_family:
  toolset:
  workflow:
  executor:
  mode: plan | execute | audit | review | research

cross_model_context:
  builder_model:
  builder_model_family:
  auditor_model:
  auditor_model_family:
  cross_model_audit_state: DISTINCT | SAME-FAMILY-BY-CHOICE | SAME-FAMILY-UNAVAILABLE | NOT-RECORDED
  cross_model_reason:
```

The Launcher, not the agent prose, should capture model family whenever possible. If the Launcher cannot capture it, the workflow must set `cross_model_audit_state: NOT-RECORDED`, which causes Premortem Plus audit rejection until fixed.

### Cross-Model State Derivation

| Condition | Derived state |
|---|---|
| Builder family and Auditor family are both known and different | `DISTINCT` |
| Both are known and same, while another approved auditor family is available | `SAME-FAMILY-BY-CHOICE` |
| Both are known and same, and no approved distinct auditor family is available | `SAME-FAMILY-UNAVAILABLE` |
| Either family is missing | `NOT-RECORDED` |

Digital State records this state; Premortem Plus decides its risk and verdict effect.

## Roles

| Role | Owns | Must not own |
|---|---|---|
| `prime` | routing, decomposition, authorization, gate enforcement, final parent decision | implementation, self-audit, silent bypass |
| `builder` | implementation, raw evidence, command output, diffs, mechanical trigger scan | approval, final risk scoring, parent Done |
| `auditor` | evidence judgment, acceptance criteria verification, risk verdict, cross-model state validation | code mutation, silent fixes, self-generated evidence approval |

## Architecture Invariants

| Invariant | Rule | Violation Example |
|---|---|---|
| Role separation | Builder, Auditor, and Prime have distinct ownership | Builder approves its own implementation |
| Evidence before judgment | Auditor reviews raw evidence, not claims | Auditor receives only "tests passed" summary |
| Authorization before mutation | Builder modifies files only after explicit authorization and file boundaries | Builder edits unapproved paths |
| Kanban as execution ledger | Work state and handoff decisions are recorded in Kanban | Major decisions live only in chat text |
| Spec-Kit as requirements layer | Requirements and plans live in target `specs/` artifacts | Reusable skill files contain product-specific requirements |
| Companion skills stay separate | Digital State links to Premortem Plus but does not duplicate risk logic | Risk scoring tables copied here |
| External executors are bounded | Codex/Claude/GitHub/MCP operate through explicit executor contracts | External tool runs without scope or evidence boundary |
| Model metadata is recorded | Model family is captured when audit independence matters | Auditor verdict lacks Builder/Auditor model family |
| No legacy role drift | analyst/researcher/coder/tester map to the 3-agent model | New cards assigned to `coder` or `tester` |

## Toolsets

Toolsets define allowed capability sets. They are not decorative labels.

| Toolset | Intended role | Allowed | Forbidden |
|---|---|---|---|
| `prime-safe` | prime | Kanban read/write routing, file read, git status, planning comments | project file mutation, implementation commands, parent Done without gates |
| `builder-full` | builder | terminal, file edit within boundaries, git diff, tests, evidence output, bounded external executor | broad refactor, unapproved paths, parent approval |
| `auditor-verification-safe` | auditor | read files, read diffs, run allowlisted verification commands, post verdict | mutating commands, silent fixes, snapshot updates, dependency installs |
| `research-safe` | builder or approved specialist | web/source research, source citations, evidence collection | project mutation unless separately authorized |

### Auditor Verification-Safe Allowlist

`auditor-verification-safe` means no intentional project mutation.

Allowed examples:
- `git status`
- `git diff`
- `git show`
- `npm run typecheck`
- `npm run lint` when configured not to rewrite files
- `npm test` when it does not update snapshots or tracked artifacts
- `pytest` when configured not to update snapshots or tracked artifacts
- read-only file listing/search commands

Forbidden examples:
- `npm install`, `npm update`, `pnpm install`, `uv add`, `pip install`
- migrations or database writes
- formatters that rewrite files
- snapshot update commands
- build commands known to overwrite tracked assets
- delete/move/cleanup commands
- any command touching secrets, credentials, production, deploy, or irreversible state

If a verification command unexpectedly changes tracked files, Auditor must stop, report the mutation, and return to Prime. Auditor must not silently keep or fix those changes.

## Workflows

A workflow is a preset procedure. It must define:

```yaml
name:
agent:
toolset:
executor:
entry_prompt:
allowed_actions:
stop_condition:
evidence_required:
handoff_target:
model_family_required: true | false
```

Recommended workflows:
- `prime-report`
- `spec-kit-plan`
- `builder-task`
- `codex-builder`
- `auditor-review`
- `github-pr-review`
- `premortem-check`

## Executors

An executor is the external action channel used by the selected workflow.

| Executor | How Hermes uses it | Boundary |
|---|---|---|
| `none` | Hermes only reasons/comments | No external execution |
| `local-terminal` | Runs shell commands in project cwd | Must obey toolset and file boundaries |
| `codex-cli` | Runs `codex exec` or equivalent terminal workflow | Codex is a bounded subprocess, not an unrestricted agent |
| `claude-github` | Uses GitHub issue/PR workflow for Claude Code | GitHub issue/PR is the contract boundary |
| `github-pr-review` | Requests external review on a PR | Review is evidence, not final approval |
| `mcp` | Calls configured MCP tools | Tool schema and permission policy define authority |

Hermes does not absorb external programs. It orchestrates them through Terminal, GitHub, MCP, API, or file/PR artifacts.

## Gate Enforcement

| Gate | Condition | Enforced By | Enforcement Mechanism | Bypass Allowed |
|---|---|---|---|---|
| Evidence Gate | Builder child complete with raw evidence | Prime | Parent cannot progress | Never |
| Implementation Gate | Explicit authorization + file boundaries | Prime | Builder dispatch withheld | Never |
| Audit Gate | Auditor verdict based on valid evidence | Prime | Parent cannot be marked done | Never |
| Risk Gate | Premortem Plus status/action satisfied where triggered | Prime + Auditor | Parent blocked or routed | Never |
| External Executor Gate | Executor selected and constrained before use | Prime | Executor not launched | Never |
| Model Metadata Gate | Required Builder/Auditor family captured for audit workflows | Launcher + Prime | Audit rejected if missing | Never |
| Human Decision Gate | Escalation, residual risk acceptance, destructive action, or unresolved high-impact ambiguity | User | Parent/routing card set to `blocked` | Never |

### Human Decision Gate

When Human Decision Gate is required, Prime must set the parent or routing card to `blocked`.

The block reason must include:
- `HUMAN_DECISION_REQUIRED`;
- the decision requested;
- the risk or escalation reason;
- allowed options;
- consequence of each option;
- exact condition required to unblock.

No Builder, Auditor, executor, or external tool may proceed past this gate until the user explicitly chooses an option.

## Hermes Native Status Mapping

Hermes status names must be verified against the active Hermes build before final deployment. Current public Hermes source exposes this status set:

```text
triage -> todo -> scheduled -> ready -> running -> blocked -> review -> done -> archived
```

Important nuance: `review` exists as a native status in current source, but current public issue tracking shows the normal CLI/tool lifecycle may not expose a first-class `request-review` transition everywhere yet. Therefore Digital State treats `review` as the preferred audit status **when locally available**, with an Auditor-owned child card as the safe fallback.

Prime uses fan-out:
- parent card = user-visible goal;
- child cards = stage-specific tasks owned by responsible role;
- native `review` may replace an Auditor child card only when the local Hermes build exposes a supported path into `review`.

| Workflow Stage | Preferred Native Status | Safe Fallback | Owner | Meaning |
|---|---|---|---|---|
| Triage | `triage` | `todo` | prime | Unsorted intake or new request |
| Todo | `todo` | `todo` | prime | Parent card created |
| Scheduled | `scheduled` | `ready` | prime | Dispatch queued, not yet claimable by worker |
| Ready for Builder | `ready` | `ready` | builder | Implementation/evidence task authorized |
| In Progress | `running` | `running` | assigned owner | Active claimed task |
| Builder Evidence Done | child `done` | child `done` | builder | Evidence handoff complete, not approval |
| Auditor Review | `review` | auditor child card: `ready -> running -> done` | auditor | Auditor emits verdict |
| Human Approval | `blocked` with `HUMAN_DECISION_REQUIRED` | `blocked` | prime/user | Explicit user decision required |
| Done | parent `done` | parent `done` | prime after all gates | Parent workflow complete |
| Archived | `archived` | `archived` | prime | Closed historical work |
| Blocked | `blocked` | `blocked` | authorized role | Missing evidence, authorization, risk, or user decision |

If `review` is not exposed in the active Hermes CLI/Desktop flow, do not force it. Use an Auditor-owned child card and keep the parent blocked from Done until the Auditor verdict is posted.

Fallback completion sequence:
1. Auditor posts the verdict and calls `kanban_complete()` on the Auditor-owned child card only.
2. Prime reads the verdict and confirms Evidence, Audit, Risk, Model Metadata, Executor, and Human Decision gates are satisfied.
3. Only then does Prime move the parent out of `blocked` and call `kanban_complete()` on the parent.
4. No role other than Prime may complete the parent.

Maintenance rule: keep this fallback sequence canonical. Other sections must cross-reference it instead of duplicating the full text.


## Tool Permission Matrix

| Tool / CLI | prime | builder | auditor |
|---|:---:|:---:|:---:|
| `hermes kanban` CLI | ✅ | ✅ | ✅ |
| `kanban_create()` | ✅ | ❌ | ❌ |
| `kanban_link()` | ✅ | ❌ | ❌ |
| `kanban_complete()` | ❌ parent / ✅ routing child only | ✅ child only | ✅ child only |
| `kanban_block()` | ✅ parent/routing when gate fails | ✅ owned child | ✅ owned child |
| `kanban_comment()` | ✅ | ✅ | ✅ |
| `kanban_unblock()` | ✅ only when unblock condition is satisfied | ❌ | ❌ |
| `kanban_heartbeat()` | ✅ owned running routing card only | ✅ owned running child card only | ✅ owned running review card/status only |

`kanban_heartbeat()` is liveness-only. It preserves an active claim while the owning role is working. It does not grant completion, approval, file mutation authority, or parent workflow authority.

### `kanban_complete()` Semantics

`kanban_complete()` means **owned child-stage completion**, not acceptance.

Rules:
- Builder may call `kanban_complete()` only on Builder-owned child cards after attaching raw evidence.
- Builder completion means “evidence or implementation handoff complete”; it never means approval.
- Auditor may call `kanban_complete()` only on Auditor-owned review child cards after posting an explicit verdict.
- Prime records the final parent routing decision after reading the Auditor verdict.
- Parent card completion may not occur before Evidence, Audit, Risk, Model Metadata, Executor, and Human Decision gates are satisfied.

Review routing note: if native `review` is not exposed in the active Hermes workflow, Auditor review must be represented by an Auditor-owned child card. This fallback is preferred over pretending Builder `done` equals acceptance.

## Local Concurrency Policy

### Default Mode

This policy is inactive by default beyond SQLite safety settings.

Default runtime assumption:
- one Prime;
- one Builder;
- one Auditor;
- sequential handoff;
- one active writer to project files at a time.

### Activation Rule

Multi-builder or parallel implementation rules become active only after an explicit project ADR enables multi-builder or parallel implementation mode.

If activated, Prime must enforce:
- no two running implementation child cards may have overlapping file boundaries;
- do not reimplement task claiming in Digital State; Hermes Kanban provides native CAS/WAL-backed claim and heartbeat behavior;
- stale `running` tasks must be handled through Hermes native claim/heartbeat/reclaim behavior where available;
- conflicting file-boundary requests are blocked before dispatch.

Recommended SQLite settings for local shared Kanban:

```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;
```

These settings improve local read/write behavior but do not replace explicit workflow gates.

## Spec-Kit Boundary

Spec-Kit provides structured requirements and planning artifacts:
- `specs/constitution.md`
- `specs/spec.md`
- `specs/plan.md`
- `specs/tasks.md`

Digital State consumes those artifacts to create Kanban tasks and evidence gates. It does not replace them.

## Companion Skill Loading Rules

| Companion Skill | Load When | Boundary |
|---|---|---|
| `premortem-plus` | Risk score, RPN, deterministic trigger, model-family audit state, FMEA, kill criterion, rescue action, suppression entry, or risk ledger decision is needed | Keep risk templates and scoring in Premortem Plus |
| `advisory-standard` | Conduct, confidentiality boundary, evidence hygiene, privacy, or communication conflict arises | Keep behavior/privacy rules in Advisory Standard |
| Target-project skill/docs | Product-specific architecture, implementation plan, or acceptance criteria are needed | Keep project facts in target repo/docs |

Digital State may call companion skills, but it must not absorb their detailed logic.

### Precedence on Conflict

If two skills appear to conflict on the same point, resolve in this order:

1. Project ADR / target-project spec. The most specific project decision wins when it does not violate safety, legal, or platform constraints.
2. The skill that owns the topic:
   - Premortem Plus owns risk thresholds, RPN, FMEA, kill criteria, rescue actions, risk verdicts, and risk ledger policy.
   - Advisory Standard owns conduct, privacy, evidence hygiene, communication, and least-disclosure rules.
   - Digital State owns roles, tools, routing, gates, handoffs, executors, launcher metadata, and Kanban lifecycle.
3. If the conflict remains unresolved, treat it as a Human Decision Gate and block for user adjudication.

Never silently pick one side of a governance conflict.

## Handoff Message Contracts

### Prime -> Builder

```text
[FROM: prime] [TO: builder] [CARD: <id>]
Action: EVIDENCE / IMPLEMENT
Project: <project id>
Workflow: <workflow id>
Executor: <executor id>
Builder model/family: <model> / <family>
Acceptance Criteria: <list>
File Boundaries: <allowed paths or none>
Expected Evidence: <raw logs / diffs / sources / screenshots>
Risk Handling: <none / Premortem Plus required / deterministic scan required>
Stop Condition: <when to stop>
```

### Builder -> Prime

```text
[FROM: builder] [TO: prime] [CARD: <id>]
Action: COMPLETE / BLOCK
Summary: <what was done or why blocked>
Files Modified: <list or none>
Commands Run: <exact commands>
Raw Evidence: <logs/diffs/sources/screenshots>
Risk Trigger Scan: <none / trigger found>
Executor Used: <none/local-terminal/codex-cli/etc>
Builder model/family: <model> / <family>
Blockers: <list or none>
```

### Prime -> Auditor

```text
[FROM: prime] [TO: auditor] [CARD: <id>]
Action: AUDIT
Project: <project id>
Workflow: <workflow id>
Evidence: <Builder raw evidence attached>
Acceptance Criteria: <list>
Builder model/family: <model> / <family>
Auditor model/family: <model> / <family>
Cross-model audit state: <derived state>
Risk Handling: <none / Premortem Plus status attached>
```

### Auditor -> Prime

```text
[FROM: auditor] [TO: prime] [CARD: <id>]
Action: APPROVE / APPROVE WITH WARNINGS / REJECT / ESCALATE
Summary: <one-line verdict>
Criteria Results: <per-criterion Met/Unmet>
Evidence Adequacy: Valid / Invalid
Risk & Security Audit: <findings or none>
Cross-model audit state: <state>
Required Fixes: <list or none>
```

## Extension Patterns

To add a new specialist agent:
1. Create the specialist profile.
2. Assign a toolset from this skill.
3. Define valid handoff actions.
4. Define owned Kanban stages.
5. Document the decision as a project ADR.
6. Update project `AGENTS.md`.
7. Run validation and attach raw evidence.

Adding a specialist is an architecture change. If the change affects role boundaries, tool permissions, evidence gates, model routing, or executor authority, load Premortem Plus.

## Legacy Role Mapping

| Former Role | New Owner |
|---|---|
| analyst | auditor |
| researcher | builder or approved specialist |
| coder | builder |
| tester | auditor |

Do not create new legacy cards. Any legacy status or label exists only for compatibility and should not be used for new routing.


Fallback completion sequence cross-reference: see the canonical sequence in `Hermes Native Status Mapping`.
