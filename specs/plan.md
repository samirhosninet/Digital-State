# Implementation Plan: Digital State Self-Development on Hermes

**Branch**: `digital-state/hermes-install-self-dev` | **Date**: 2026-06-20 | **Spec**: `specs/spec.md`

**Input**: Feature specification from `/specs/spec.md` (Current Project Mission) and `specs/constitution.md` Current Project Mission.

**Note**: This plan inherits the Spec-Kit template structure. The mission-specific overlay below binds every artifact to the active meta-architecture effort.

## Current Project Mission / Self-Development Scope

This is a **meta-architecture effort** with two coupled goals:

- **Goal A — Hermes-Compatible Installation**: Make Digital State install correctly onto Hermes Agent according to Hermes architecture.
- **Goal B — Reusable Overlay Update**: Update Digital State itself as a portable governance overlay (Prime / Builder / Auditor).

Execution rule (per `AGENTS.md` Source-of-Truth Priority and Spec-Kit Workflow):

- **Spec-Kit** is the requirements and planning source.
- **Kanban** is the execution and audit source. Every child task is created by Prime and routed through the Evidence, Implementation, and Audit gates (Constitution Article IV).
- **Digital State + Premortem Plus** skills are mandatory baseline context per Constitution Article IX.
- **Profile isolation** is non-negotiable: Prime / Builder / Auditor are real Hermes profiles per Constitution Article III. Generic subagents cannot substitute for these profiles in governed work.

User architectural directives become durable architecture only after they are recorded in `specs/constitution.md`, `AGENTS.md`, and the relevant Spec-Kit artifact (Constitution Article I). Implementation files for governance changes must be scoped via Kanban file boundaries (Constitution Article VI).

## Universal Reusable Overlay Scope

> **Principle**: Digital State is a universal reusable governance
> overlay. The plan MUST end with a reusable package that installs
> correctly on **any** target project — public, private, internally
> hosted, vendor-delivered, monorepo, solo repo, regulated — without
> modification of the reusable framework files. (Constitution Article
> XI; user clarification 2026-06-20.)

### Plan-level obligations derived from the Universal Overlay Scope

- The reusable package (installer, validator, governance files,
  baseline skills, distribution manifest) treats target path,
  target repository, target Kanban database, and target Spec-Kit
  root as **runtime parameters**, not as compiled-in defaults.
- The installer MUST be able to onboard an empty target workspace
  without importing any state from the `D:/digital-state` source
  workspace or any other prior target.
- Implementation Kanban cards for the reusable package MUST declare
  file boundaries that stay inside the reusable framework — no
  card may silently pull in target-specific paths, card IDs, repo
  names, branches, or product requirements.
- Verification of a reusable release MUST include a clean-room
  install / validate run against an empty test target to catch
  accidental target coupling.

### Boundary test

A reusable Digital State release is valid only if its installer
and governance files can be applied to a brand-new target
workspace with no historical awareness of any prior target.
Hard-coding state that only fits one target is a Constitution
violation (Article XI).

### Compatibility with the current Self-Development mission

The active Self-Development mission (Goal A — Hermes-Compatible
Installation, Goal B — Reusable Overlay Update) is the
**first instance** of the universal overlay contract; the deliverable
is a reusable package that satisfies Article XI for **all**
subsequent target installations, not only for the originating
`D:/digital-state` workspace.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (__SPECKIT_COMMAND_PLAN__ command output)
├── research.md          # Phase 0 output (__SPECKIT_COMMAND_PLAN__ command)
├── data-model.md        # Phase 1 output (__SPECKIT_COMMAND_PLAN__ command)
├── quickstart.md        # Phase 1 output (__SPECKIT_COMMAND_PLAN__ command)
├── contracts/           # Phase 1 output (__SPECKIT_COMMAND_PLAN__ command)
└── tasks.md             # Phase 2 output (__SPECKIT_COMMAND_TASKS__ command - NOT created by __SPECKIT_COMMAND_PLAN__)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
