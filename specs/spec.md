---
description: "Digital State Self-Development on Hermes"
---

# Feature Specification: Digital State Self-Development on Hermes

**Feature Branch**: `digital-state/hermes-install-self-dev`

**Created**: 2026-06-20

**Status**: Active — in-progress mission

**Input**: User clarification (Arabic, 2026-06-20): the active work is a meta-architecture effort to inspect, modify, update, and develop Digital State itself so that it can later install correctly onto Hermes Agent, while simultaneously upgrading Digital State's own governance architecture.

## Current Project Mission

This is a **meta-architecture effort**. Two goals operate together:

- **Goal A — Hermes-Compatible Installation**: Make Digital State install onto Hermes Agent according to Hermes architecture.
- **Goal B — Reusable Overlay Update**: Update Digital State itself as a portable governance overlay (Prime / Builder / Auditor).

Source-layer rule (per `specs/constitution.md` Article II and `AGENTS.md` Source-of-Truth Priority):

- **Spec-Kit** (this file, `spec.md`, `plan.md`, `constitution.md`) is the **requirements and planning source**.
- **Kanban** is the **execution and audit source** — no durable decision lives only in chat.
- **Digital State + Premortem Plus** skills are mandatory baseline context for every Digital State profile (Constitution Article IX).
- Every agent is a **real, isolated Hermes profile** (`prime`, `builder`, `auditor`) with its own role, tools, permissions, skills, and model configuration — never a generic `delegate_task` subagent (Constitution Article III).

User architectural directives become durable architecture only after they are recorded in project files under §Durable Governance Directives in `AGENTS.md` and the relevant Spec-Kit artifact (Constitution Article I).

## Universal Reusable Overlay Scope

> **Principle**: Digital State is a universal reusable governance
> overlay. The same Prime / Builder / Auditor framework MUST install
> correctly on **any** target project — public, private, internally
> hosted, vendor-delivered, monorepo, solo repo, regulated — without
> modification of the reusable framework files. (Constitution Article
> XI; user clarification 2026-06-20: Digital State must later work on
> any project: public, private, or any other target.)

### Scope statements

- The reusable Digital State package contains only **project-agnostic**
  governance, profile roles, installer / validator logic, baseline
  skills, distribution manifest, and templates.
- Reusable framework files MUST NOT hard-code target-project paths,
  repository names, branches, Hermes Kanban card IDs, migration
  state, model / provider choices, or product-specific requirements.
- Target-product requirements, user stories, technical context, and
  success criteria for a specific project live in **that
  target workspace's own Spec-Kit files** under its `specs/`
  directory and are owned by that target project's operator.
- Target execution state, evidence, approvals, blocks, verdicts, and
  the audit trail for governed work live in **that target
  workspace's own Hermes Kanban board** (`kanban.db` plus the
  parent / child card graph), not in static reusable files and not
  in chat.
- Target-project risk register (`risk-ledger.md` or equivalent) lives
  in the target workspace per `skills/premortem-plus/SKILL.md`; the
  reusable framework only defines the integration link.

### Boundary test

A reusable Digital State release is valid only if its installer and
governance files can be applied to a brand-new target workspace
with no historical awareness of any prior target. Hard-coding
state that only fits one target is a Constitution violation
(Article XI).

### Compatibility with the current Self-Development mission

The Self-Development mission (Goal A — Hermes-Compatible
Installation, Goal B — Reusable Overlay Update) is the **first
instance** of the universal overlay contract: Digital State is
developing itself on Hermes so that the resulting reusable package
satisfies Article XI and can be installed cleanly on every other
target afterwards. This spec therefore serves dual purpose:

1. Capture the active meta-architecture development work for the
   `D:/digital-state` workspace (Current Project Mission above).
2. Define the universal reusable overlay contract that any future
   target — public, private, or arbitrary — will adopt
   (`AGENTS.md` + Spec-Kit files + Kanban integration + baseline
   skills) without inheriting this workspace's specific state.

## User Scenarios & Testing

### User Story 1 — Clean Install on Fresh Hermes (Priority: P1)

As a project operator, I want to run `install.ps1` on a fresh Hermes Agent installation and have all three profiles (prime, builder, auditor) fully configured with correct Kanban concurrency cap, toolsets, model, skills, SOUL.md, and audit-matrix plugin — so that I can immediately start governed work without manual configuration.

**Why this priority**: Without a working installer, nothing else matters. This is the minimum viable product of Digital State — it must install correctly before any governance cycle can run.

**Independent Test**: Can be fully tested by deleting all three Hermes profiles (or using a clean test profile directory), running `install-simple.ps1`, then verifying: (1) `hermes -p prime kanban list` succeeds, (2) `hermes -p auditor plugins list` shows audit-matrix, (3) each profile's config.yaml contains `kanban.max_in_progress_per_profile: 1`, (4) SOUL.md files are present and syntactically valid, (5) baseline skills are discoverable via `hermes -p <profile> skills list`.

**Acceptance Scenarios**:

1. **Given** a fresh Hermes Agent 0.14.0+ installation with no Digital State profiles, **When** operator runs `install-simple.ps1`, **Then** three profiles (prime, builder, auditor) are created with correct config.yaml, SOUL.md, skills, and plugin registration.
2. **Given** an existing Hermes installation with stale Digital State profiles, **When** operator re-runs `install-simple.ps1`, **Then** existing profiles are backed up to `%LOCALAPPDATA%\hermes\backups\` before overwrite, and new profiles are written correctly (idempotent).
3. **Given** installed profiles, **When** operator runs `validate-final.ps1`, **Then** script exits with code 0 and reports all checks passed.
4. **Given** installed profiles, **When** operator checks any profile's `config.yaml`, **Then** `kanban.max_in_progress_per_profile: 1` is present and correct (Constitution Article XIII).

---

### User Story 2 — End-to-End Governance Cycle (Priority: P1)

As a project operator, I want to create a Kanban parent card, have Prime route it to Builder for evidence, Builder complete with raw logs, Prime promote to review for Auditor, Auditor issue a verdict, and Prime record the final decision — so that the full Digital State governance lifecycle works correctly.

**Why this priority**: The governance cycle IS Digital State. If the Builder→Auditor handoff, the `review-required` block, the Prime `blocked → review` promotion, and the Auditor verdict don't work, the framework is just documentation.

**Independent Test**: Can be fully tested by creating a single parent card via `hermes kanban create`, running the full cycle manually once, and checking: (1) Builder produces evidence with raw logs, (2) Builder blocks with `review-required:` reason, (3) Prime (or operator) promotes card to `status='review'`, (4) Dispatcher picks up the card and spawns auditor, (5) Auditor returns APPROVE or REJECT with verdict, (6) Prime records on parent.

**Acceptance Scenarios**:

1. **Given** a parent card in `todo` status, **When** Prime creates a Builder child task, **Then** Builder picks up the card, gathers evidence, and blocks with `reason="review-required: <evidence summary>"`.
2. **Given** a Builder implementation card in `blocked` status with `review-required:` reason, **When** Prime promotes to `status='review'` and reassigns to `auditor`, **Then** the Hermes dispatcher picks up the card and spawns the auditor profile.
3. **Given** an Auditor review in progress, **When** Auditor issues `APPROVE`, **Then** Prime records the verdict on the parent card as `kanban_comment()` and the card reaches `done`.
4. **Given** an Auditor review in progress, **When** Auditor issues `REJECT: <reason>`, **Then** Prime re-routes the card back to `running` for Builder remediation with the Auditor's reason attached.

---

### User Story 3 — Audit-Matrix Multi-Lens Review (Priority: P2)

As an Auditor operator, I want to invoke `/auditor-matrix <card_id>` and have three independent auditor lenses (criteria, risk, constitutional) each run with distinct models, then adjudicate their verdicts into a single matrix verdict according to the policy file — so that I get multi-perspective audit coverage without manual orchestration.

**Why this priority**: Multi-lens review is the quality differentiator of Digital State over single-model auditing. It's not needed for the basic cycle but is critical for production-grade assurance.

**Independent Test**: Can be tested by installing the audit-matrix plugin on the auditor profile, running `/auditor-matrix <card_id>` on a review card, and checking: (1) three one-shot sessions spawn with different models, (2) each returns an individual verdict, (3) the policy adjudicates correctly, (4) no config.yaml or SOUL.md is mutated.

**Acceptance Scenarios**:

1. **Given** audit-matrix plugin is loaded on the auditor profile, **When** operator invokes `/auditor-matrix <card_id>`, **Then** three auditor lenses spawn with their configured models and each returns a verdict.
2. **Given** three individual verdicts, **When** the policy adjudicates, **Then** the matrix verdict follows the rules in `governance/audit-matrix-policy.yaml` (any REJECT → matrix REJECT, all APPROVE → matrix APPROVE, mixed → WARN).
3. **Given** a `--dry-run` flag, **When** operator invokes `/auditor-matrix <card_id> --dry-run`, **Then** the command shows what would be executed without spawning any sessions.
4. **Given** a `--policy PATH` override, **When** operator invokes with a custom policy file, **Then** the custom policy is used instead of the default discovery chain.

---

### User Story 4 — Portable Plugin with No Hardcoded Paths (Priority: P2)

As a project operator installing Digital State on a different machine, I want the audit-matrix plugin to discover its policy file via environment variables (`$DIGITAL_STATE_HOME`, `$HERMES_HOME`) instead of hardcoded Windows absolute paths — so that the plugin works on any system without editing source code.

**Why this priority**: Portability is a Constitution Article XI requirement. Hardcoded paths are the #1 reason overlays fail on new targets.

**Independent Test**: Install Digital State on a machine where `C:\Users\seo` does not exist; set `$DIGITAL_STATE_HOME` to the install location; run `hermes -p auditor plugins list` and verify audit-matrix loads without file-not-found errors.

**Acceptance Scenarios**:

1. **Given** `$DIGITAL_STATE_HOME` is set to a valid path, **When** audit-matrix plugin loads, **Then** it discovers `governance/audit-matrix-policy.yaml` under that path without errors.
2. **Given** `$DIGITAL_STATE_HOME` is unset and `$HERMES_HOME` is set, **When** audit-matrix plugin loads, **Then** it falls back to `$HERMES_HOME/governance/audit-matrix-policy.yaml`.
3. **Given** all environment variables are unset, **When** audit-matrix plugin loads, **Then** it falls back to `./governance/audit-matrix-policy.yaml` relative to the current directory.
4. **Given** plugin `__init__.py`, **When** inspected, **Then** no hardcoded `C:\Users\seo` or equivalent absolute path exists anywhere in the source.

---

### User Story 5 — Risk Governance Flow (Priority: P3)

As a project operator, I want to trigger a Premortem Plus risk assessment on a task, have the risk recorded in `risk-ledger.md`, and be blocked from proceeding until the risk is mitigated or accepted — so that no irreversible action bypasses risk governance.

**Why this priority**: Risk governance is essential but depends on the governance cycle (US2) and installer (US1) being operational first. It is also harder to test end-to-end without a real risk scenario.

**Independent Test**: Create a Kanban card that touches an irreversible operation (e.g., deployment), verify: (1) Premortem Plus status is triggered, (2) entry appears in risk-ledger.md, (3) card is blocked until risk is resolved, (4) unblock requires risk-acceptance sign-off.

**Acceptance Scenarios**:

1. **Given** a card that touches irreversible operations, **When** Builder or Auditor identifies a risk trigger, **Then** a `Premortem Status: TRIGGERED: <reason>` line is required on the card.
2. **Given** a triggered risk, **When** the risk is assessed, **Then** an entry is created in `risk-ledger.md` with ID, description, severity, status, owner, and date.
3. **Given** a high-severity unmitigated risk, **When** the card is reviewed, **Then** progress is blocked until mitigation is documented or a risk-acceptance sign-off is recorded.
4. **Given** a low-severity risk, **When** Auditor evaluates, **Then** the risk may be accepted or suppressed per Premortem Plus rules with documented rationale.

---

### Edge Cases

- What happens when both `$DIGITAL_STATE_HOME` and `$HERMES_HOME` point to invalid paths? → Plugin should log a clear error and fall back to `./governance/` before failing.
- What happens when the Hermes Kanban board does not expose `status='review'`? → Fall back to the child-Auditor-card path and record the deviation on the parent card per Constitution Article XIV.
- What happens when `install.ps1` is run twice on the same profiles? → Idempotent — backup existing profiles, overwrite cleanly, no duplicate entries.
- What happens when Builder's model hits a rate limit mid-task? → Builder blocks with `reason="rate-limit: retry after X seconds"` and Prime re-dispatches after cooldown.
- What happens when Auditor crashes during review? → Operator restarts the auditor profile and picks up the same review card (the `task_runs` row is independent per `claim_review_task`).
- What happens when `validate-final.ps1` finds a concurrency cap violation? → Exit code non-zero, specific profile and missing key reported, installation not treated as correct per Article XIII.

## Requirements

### Functional Requirements

- **FR-001**: The installer (`scripts/install.ps1` and `scripts/install-simple.ps1`) MUST create three Hermes profiles (`prime`, `builder`, `auditor`) with correct `config.yaml`, `SOUL.md`, skill files, and plugin registration on a fresh Hermes Agent 0.14.0+ installation.
- **FR-002**: Every profile's `config.yaml` MUST contain `kanban.max_in_progress_per_profile: 1` — the installer and validator MUST enforce this (Constitution Article XIII).
- **FR-003**: The installer MUST be idempotent — re-running on existing profiles MUST create backups before overwrite and produce identical end state.
- **FR-004**: The `validate-final.ps1` script MUST verify all profile configs, skill presence, plugin loadability, SOUL.md validity, distribution consistency, and version alignment — exiting non-zero on any failure.
- **FR-005**: The audit-matrix plugin MUST discover its policy file via the environment variable chain (`$DIGITAL_STATE_HOME`, `$HERMES_DIGITAL_STATE_HOME`, `$HERMES_HOME`, `./`) with no hardcoded absolute paths.
- **FR-006**: All three baseline skills (`digital-state`, `premortem-plus`, `advisory-standard`) MUST be available to every profile via `hermes -p <profile> skills list`.
- **FR-007**: The Builder → Auditor handoff MUST follow the canonical Phase B path: Builder blocks with `review-required:` reason, Prime promotes the same card to `status='review'`, Hermes dispatcher spawns the auditor profile.
- **FR-008**: The Auditor MUST issue one binding verdict per review: `APPROVE`, `APPROVE WITH WARNINGS`, `REJECT: <reason>`, or `ESCALATE: <reason>`.
- **FR-009**: Prime MUST NOT dispatch a second concurrent task on any profile when one is already running (Kanban concurrency cap = 1).
- **FR-010**: Risk entries for triggered Premortem Plus assessments MUST be recorded in `risk-ledger.md` with ID, description, severity, status, owner, date, and review columns.
- **FR-011**: Reusable framework files (`AGENTS.md`, `SOUL.md` files, skills, plugin source) MUST NOT contain target-project-specific paths, card IDs, repository names, or model/provider choices.
- **FR-012**: All governance file changes (constitution, AGENTS.md, SOUL.md, skill manifests, distribution.yaml) MUST increment version in YAML frontmatter, add a CHANGELOG.md entry, and pass Builder → Auditor review before taking effect (Constitution Article VIII).

### Key Entities

- **Profile**: A Hermes Agent profile (prime, builder, auditor) with config.yaml, SOUL.md, skills, and optional plugins. Owned by the installer.
- **Kanban Card**: A task record in `kanban.db` with status, assignee, claim lock, and dependency edges. Used for all execution and audit state.
- **Skill**: A reusable `SKILL.md` file with optional `references/`, `templates/`, and `scripts/` directories. Installed per-profile.
- **Plugin**: A Hermes plugin (e.g., audit-matrix) with `plugin.yaml` manifest, Python source, and policy file. Installed per-profile.
- **Risk Entry**: A row in `risk-ledger.md` representing a tracked risk with ID, description, severity, status, owner, date, and review status.
- **Distribution Manifest**: `distribution.yaml` declaring version, owned files, and compatibility constraints.

## Success Criteria

### Measurable Outcomes

- **SC-001**: `install-simple.ps1` on a fresh Hermes installation produces three working profiles in under 60 seconds with zero manual configuration steps.
- **SC-002**: `validate-final.ps1` exits with code 0 on a clean install and exits non-zero on any profile missing the concurrency cap key or any required file.
- **SC-003**: A complete Builder → review-required → Prime promotion → Auditor verdict cycle completes on a test card within a single session with all transitions recorded in `kanban.db`.
- **SC-004**: `grep -r "C:\\\\Users\\\\seo" skills/ plugins/ profiles/ governance/` returns zero matches (no hardcoded local paths in reusable files).
- **SC-005**: `hermes -p auditor plugins list` shows audit-matrix loaded and functional on any machine with `$DIGITAL_STATE_HOME` or `$HERMES_HOME` set correctly.
- **SC-006**: Three baseline skills appear in `hermes -p <profile> skills list` for every profile after installation.

## Assumptions

- Hermes Agent version 0.14.0+ is installed and functional on the target machine.
- PowerShell 5.1+ is available for Windows installation scripts.
- Python 3.11+ is available for plugin execution and validation tools.
- The operator has write access to the Hermes profiles directory and Kanban database.
- Model API access (nvidia provider) is available for the configured models.
- Environment variables (`$DIGITAL_STATE_HOME`, `$HERMES_HOME`) may or may not be set — the installer and plugin must handle both cases gracefully.
