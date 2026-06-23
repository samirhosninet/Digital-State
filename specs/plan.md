# Implementation Plan: Digital State Self-Development on Hermes

**Branch**: `digital-state/hermes-install-self-dev` | **Date**: 2026-06-20 | **Spec**: `specs/spec.md`

**Input**: Feature specification from `specs/spec.md` (Current Project Mission) and `specs/constitution.md` (Articles I–XV).

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

Digital State is a self-developing meta-architecture: it must install onto Hermes Agent (Goal A) while simultaneously upgrading its own governance overlay (Goal B). The technical approach is: PowerShell-based installer for profile creation, SQLite-based Kanban for execution state, three isolated Hermes profiles with mandatory baseline skills, and a native `review` status handoff for the Builder → Auditor lifecycle. The deliverable is a reusable package that passes `validate-final.ps1` clean-room install and supports end-to-end governance cycles.

## Technical Context

**Language/Version**: Python 3.11+ (plugin logic, validation), PowerShell 5.1+ (installer), Bash/MSYS (Hermes CLI interaction on Windows)

**Primary Dependencies**: Hermes Agent ≥0.14.0, `hermes` CLI (kanban, profiles, plugins, skills subcommands), `specify-cli` v0.11.5 (Spec-Kit)

**Storage**: SQLite (`kanban.db`) via Hermes Kanban subsystem; filesystem-based profile/skill/plugin installation; `risk-ledger.md` as Markdown table

**Testing**: `scripts/validate-final.ps1` (structural + config validation), manual end-to-end governance cycle via `hermes kanban create/list/show` commands, `hermes -p <profile> plugins list` for plugin load check, `hermes -p <profile> skills list` for skill availability

**Target Platform**: Windows 10+ with Git Bash / MSYS (Hermes Agent runs on Linux via WSL or native; current deployment is Windows-native with bash shell)

**Project Type**: Governance overlay / meta-architecture framework (library + installer + configuration package — no runtime server)

**Performance Goals**: Installer completes in <60 seconds on fresh Hermes install. Governance cycle (create parent → Builder evidence → review → Auditor verdict → Done) completes within a single operator session. Plugin multi-lens review spawns three one-shots concurrently and adjudicates in <5 minutes.

**Constraints**: No hardcoded absolute paths in reusable files. No model/provider choices in framework files. Kanban concurrency cap = 1 per profile enforced at installer and config level. All governance changes require version bump + CHANGELOG + Builder → Auditor review (Constitution Article VIII).

**Scale/Scope**: 3 agent profiles, 3 baseline skills, 1 plugin (audit-matrix), 1 installer, 1 validator, ~30 governance/framework files. Target: any number of downstream projects installing this overlay.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Topic | Status | Notes |
|---------|-------|--------|-------|
| I | Source of Truth | ✅ Pass | Spec-Kit + Kanban are defined as sources; user directives recorded in AGENTS.md |
| II | Advisory Standard | ✅ Pass | advisory-standard skill exists and is referenced in all SOUL.md files |
| III | Profile Isolation | ✅ Pass | Three isolated Hermes profiles with independent config/SOUL/skills |
| IV | Core Operating Rule | ✅ Pass | Builder→Auditor→Prime separation enforced in SOUL.md and AGENTS.md |
| V | Evidence Gate | ✅ Pass | Raw logs required before Auditor review |
| VI | Implementation Gate | ✅ Pass | File boundaries and authorization required before Builder implementation |
| VII | Audit Gate | ✅ Pass | No parent Done without Auditor APPROVE |
| VIII | Version Governance | ✅ Pass | Version bump + CHANGELOG + review required for governance changes |
| IX | Mandatory Baseline Skills | ✅ Pass | digital-state, premortem-plus, advisory-standard listed in all SOUL.md |
| X | Concurrency Policy | ✅ Pass | `max_in_progress_per_profile: 1` in all config.yaml |
| XI | Kanban as Execution Ledger | ✅ Pass | All work state recorded in kanban.db |
| XII | Spec-Kit as Requirements Layer | ✅ Pass | Requirements in specs/ files, not in framework files |
| XIII | Binding Installation Guarantee | ✅ Pass | Installer sets concurrency cap; validator checks it; SOUL.md Protocol validates it |
| XIV | Native Review Status | ✅ Pass | `review-required` block → Prime promotion → `status='review'` documented |
| XV | Risk Gate | ✅ Pass | Premortem Plus integration documented; risk-ledger.md template exists |

## Project Structure

### Documentation (this feature)

```text
specs/
├── constitution.md     # Governance articles I–XV
├── spec.md             # Feature specification (this file)
├── plan.md             # Implementation plan (this file)
└── tasks.md            # Task list with phases and checkboxes
```

### Source Code (repository root)

```text
digital-state/
├── AGENTS.md                          # Project context for all agents
├── CHANGELOG.md                       # Version history
├── PACKAGE.md                         # Install options and verification
├── README.md                          # Quick start
├── risk-ledger.md                     # Risk register
├── distribution.yaml                  # Package manifest
│
├── specs/                             # Spec-Kit artifacts
│   ├── constitution.md
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
│
├── profiles/                          # Hermes Agent profiles
│   ├── prime/
│   │   ├── config.yaml                # Model, kanban cap, toolsets
│   │   └── SOUL.md                    # Prime identity and protocol
│   ├── builder/
│   │   ├── config.yaml
│   │   └── SOUL.md
│   └── auditor/
│       ├── config.yaml
│       └── SOUL.md
│
├── plugins/
│   └── audit-matrix/                  # Multi-lens auditor plugin
│       ├── __init__.py                # Plugin entry + hooks
│       ├── matrix.py                  # Adjudication logic
│       ├── policy.py                  # Policy discovery + loading
│       ├── plugin.yaml                # Plugin manifest
│       └── README.md
│
├── skills/                            # Mandatory baseline skills
│   ├── advisory-standard/
│   │   └── SKILL.md
│   ├── digital-state/
│   │   └── SKILL.md
│   └── premortem-plus/
│       └── SKILL.md
│
├── governance/
│   └── audit-matrix-policy.yaml       # Multi-lens adjudication policy
│
├── scripts/
│   ├── install.ps1                    # Full installer with error handling
│   ├── install-simple.ps1             # Streamlined fallback installer
│   ├── validate-final.ps1             # Post-install validation
│   ├── uninstall.ps1                  # Uninstaller with backup discovery
│   └── promote-to-review.sh           # CLI for blocked→review promotion
│
├── tests/                             # Automated test suite (pytest)
│   ├── conftest.py
│   ├── test_version_sync.py
│   ├── test_concurrency_cap.py
│   ├── test_gates.py
│   ├── test_kanban_block_to_review.py
│   ├── test_risk_ledger.py
│   ├── test_validate_final.py
│   └── test_smoke_hermes_cli.py
│
├── Makefile                           # Unified command targets
├── .gitignore
├── .github/                           # Community templates
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       └── ci.yml
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── docs/                              # Additional documentation
│   └── samples/                       # Example install and governance cycle
│       └── clean-room-install.md
│
└── scripts/
    ├── install.ps1                    # Full installer with error handling
    ├── install-simple.ps1             # Streamlined fallback installer
    └── validate-final.ps1             # Post-install validation
```

**Structure Decision**: Governance overlay with automated regression via `tests/` pytest suite and CLI-driven smoke tests. Validation is performed by both `validate-final.ps1` (structural) and `pytest tests/ -v` (behavioral). The plugin is the only Python code and is installed as a Hermes plugin (not a standalone package).

## Execution Phases

### Phase 1: Infrastructure (T001–T005) ✅ DONE
Project initialized, version control, clean workspace.

### Phase 2: Plugin Fix (T008–T011)
Fix hook references, portability, phantom task, and test plugin load.

### Phase 3: Profile Configuration (T015–T017)
Add toolsets, verify concurrency cap, test profile spawn.

### Phase 4: Skills Integration (T018–T027)
Verify skill content, add skill loading to SOUL.md, create handoff templates, validate integration via Builder → Auditor.

### Phase 5: Kanban Wiring (T028–T037)
Spec-Kit artifacts already exist (T028–T031 done); verify Kanban toolset, test board creation, test review handoff, update AGENTS.md.

### Phase 6: Risk Governance (T039–T048)
Create risk-ledger.md entries, add Premortem Plus triggers, implement Risk Status line, create threat model and FMEA templates, define kill criteria.

### Phase 7: Installation & Validation (T049–T058)
Rewrite installer with robust error handling, validate concurrency cap, test clean install, test backup feature, add version bump validation.

### Phase 8: Governance & Versioning (T059–T068)
Implement Article VIII enforcement, create documentation, review AGENTS.md/constitution consistency, add Arabic handoff template, create community files.

### Phase 9: Quality Assurance (T069–T078)
Full governance cycle test, individual gate tests, concurrency cap test, profile isolation test, final validation.

### Phase 10: Hardening & Release (T079–T087)

**Goal**: Close open risks, add automated regression protection, remove portable-overlay violations, and establish a clean release path.

**Rationale**: Phases 1–9 delivered a working governance overlay (v3.2.0). The risk ledger carries two High-severity open items (RISK-001: no CLI for blocked→review promotion; RISK-002: installer quoting bug — now fixed). The package hardcodes model/provider choices in config.yaml (overlay portability violation), lacks an uninstaller, has no automated test suite, and the audit-matrix plugin has no functional smoke test. Phase 10 addresses all of these before the project can be considered production-ready.

**Constraints**:
- No new governance articles — Phase 10 operates within the existing Articles I–XV.
- All changes follow Article VIII (version bump + CHANGELOG + Builder→Auditor review).
- File boundaries: new files under `tests/`, `scripts/`, and edits to `risk-ledger.md`, `specs/`, `profiles/*/config.yaml`, `CHANGELOG.md`.
- No breaking changes: existing installer and validator must continue to pass.

## Complexity Tracking

No constitution violations requiring justification. All decisions follow the existing article framework.
