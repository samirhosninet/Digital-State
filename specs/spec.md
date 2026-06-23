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

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
