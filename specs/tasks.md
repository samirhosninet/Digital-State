---
description: "Digital State Self-Development Tasks"
---
# Tasks: Digital State Governance Overlay

**Input**: `specs/spec.md` (Goals A/B), `specs/plan.md` (Technical Context), `specs/constitution.md` (Articles I–XV)

**Prerequisites**: Hermes Agent, `specify init .` (Spec-Kit v0.11.5)

**Tests**: validate-final.ps1 (run after any infrastructure change)

---

## Phase 1: Infrastructure & Setup

**Goal**: Project initialized, version control, clean workspace

- [x] T001 Create `.gitignore` with Python, Hermes, and IDE exclusions
- [x] T002 Initialize Git repository (`git init`)
- [x] T003 Install Spec-Kit CLI v0.11.5 (`uv tool install specify-cli`)
- [x] T004 Initialize Spec-Kit inside digital-state (`specify init .`)
- [x] T005 Create `profiles/*/config.yaml` for prime/builder/auditor (minimal: model, kanban cap)

---

## Phase 2: Plugin System (audit-matrix)

**Goal**: `plugins/audit-matrix/` functional and installable

- [x] T006 Copy audit-matrix plugin files into `D:\\digital-state\\plugins\\audit-matrix\\`
- [x] T007 Verify plugin manifest (`plugin.yaml`) structure
- [ ] T008 Fix hook references in `__init__.py` (pre_chat → on_session_start)
- [ ] T009 Make policy path portable (remove hardcoded `C:\\Users\\seo\\...`)
- [ ] T010 Fix phantom task reference in plugin init
- [ ] T011 Test plugin load via `hermes -p auditor plugins list`

---

## Phase 3: Profile Configuration

**Goal**: prime/builder/auditor profiles ready for install

- [x] T012 Create `profiles/prime/config.yaml` (kanban cap: 1, model: nemotron)
- [x] T013 Create `profiles/builder/config.yaml` (kanban cap: 1, model: nemotron)
- [x] T014 Create `profiles/auditor/config.yaml` (kanban cap: 1, audit-matrix enabled)
- [ ] T015 Add toolsets block to all three configs.yaml (`- kanban` mandatory)
- [ ] T016 Verify `kanban.max_in_progress_per_profile: 1` in each config.yaml (Article XIII Gate)
- [ ] T017 Test profile spawn: `hermes -p prime chat -q "test"`

---

## Phase 4: Skills Integration (Tasks 018-027)

- [ ] 018 Verify skills/digital-state/SKILL.md contains governance reference, handoff templates, tool permissions
- [ ] 019 Verify skills/premortem-plus/SKILL.md contains risk governance, kill criteria, rescue actions, FMEA
- [ ] 020 Verify skills/advisory-standard/SKILL.md contains behavioral, privacy, evidence-hygiene baseline
- [ ] 021 Add skill loading to each profile's SOUL.md Protocol (Mandatory Baseline Skills step)
- [ ] 022 Test skill availability: `hermes -p prime skills list` should show all three skills
- [ ] 023 Create handoff templates in skills/digital-state/references/handoff-template.md
- [ ] 024 Update AGENTS.md §Handoff Protocol with standardized format
- [ ] 025 Implement risk-ledger.md template in skills/premortem-plus/references/
- [ ] 026 Add Premortem Status line requirement to skills/premortem-plus/SKILL.md
- [ ] 027 Validate skill integration via Builder → Auditor review of a test task

## Phase 5: Kanban & Spec-Kit Wiring (Tasks 028-038)

- [ ] 028 Create specs/constitution.md with Articles I–XV (current)
- [ ] 029 Create specs/spec.md with Goals A/B (Hermes-Compatible Installation, Reusable Overlay Update)
- [ ] 030 Create specs/plan.md with technical context ( Hermes Agent 0.14.0+, Windows PowerShell, Python 3.11)
- [ ] 031 Create initial specs/tasks.md (this file)
- [ ] 032 Verify Kanban toolset availability: `hermes tools list` shows kanban as built-in
- [ ] 33 Test Kanban board creation: `hermes kanban boards list`
- [ ] 34 Create initial parent card via `hermes kanban create` assigned to prime
- [ ] 35 Test handoff: block card with review-required, promote to review via direct DB write (simulate)
- [ ] 36 Verify dispatcher auto-spawns auditor on review status
- [ ] 37 Update AGENTS.md §Kanban Board with native statuses and workflow stage mapping

## Phase 6: Risk Governance (Tasks 039-048)

- [ ] 039 Create risk-ledger.md with template columns: ID, Description, Severity, Status, Owner, Date, Review
- [ ] 040 Add Premortem Plus risk triggers to skills/premortem-plus/SKILL.md (deterministic triggers, irreversible operations)
- [ ] 041 Implement Risk Status line in tasks: `## Premortem Status: [NOT_TRIGGERED|TRIGGERED: <reason>]`
- [ ] 042 Add Risk Ledger handling requirement: every risk must have entry in risk-ledger.md
- [ ] 043 Create threat modeling prompts in skills/premortem-plus/references/threat-model.md
- [ ] 044 Add FMEA worksheet to skills/premortem-plus/references/fmea-template.xlsx
- [ ] 045 Define kill criteria and rescue actions in skills/premortem-plus/SKILL.md
- [ ] 046 Test risk flow: trigger a risk, record in risk-ledger.md, require mitigation before proceeding
- [ ] 047 Update AGENTS.md §Premortem Plus Risk Governance with procedural steps
- [ ] 048 Verify Article XV (Risk Gate) enforced in specs/constitution.md

## Phase 7: Installation & Validation (Tasks 049-058)

- [ ] 049 Rewrite scripts/install.ps1 with robust error handling and idempotency
- [ ] 050 Add Install-Profiles, Install-Plugins, Install-Governance, Validate-Installation functions
- [ ] 051 Ensure installer sets kanban.max_in_progress_per_profile=1 for all profiles (Article XIII)
- [ ] 052 Create scripts/install-simple.ps1 as fallback without complex model config
- [ ] 053 Update scripts/validate-final.ps1 to check config.yaml for concurrency cap
- [ ] 054 Test clean install: delete Hermes profiles, run install-simple.ps1, verify profiles work
- [ ] 055 Test installer backup feature: verify backups created in %LOCALAPPDATA%\hermes\backups\
- [ ] 056 Validate tool profiles: prime has minimal toolset, builder has web/terminal, auditor has web/terminal
- [ ] 057 Add version bump validation to validate-final.ps1 (check distribution.yaml version matches)
- [ ] 058 Document installation process in PACKAGE.md and README.md

## Phase 8: Governance & Versioning (Tasks 059-068)

- [ ] 059 Implement Article VIII: version bump + CHANGELOG entry + Builder→Auditor review for all governance changes
- [ ] 060 Create PACKAGE.md with install options, tool policy, verification steps
- [ ] 061 Update CHANGELOG.md with entries for v3.1.1 through v3.1.7
- [ ] 062 Update README.md with current version and quick start instructions
- [ ] 063 Review and fix AGENTS.md for consistency with constitution.md articles
- [ ] 064 Add Arabic/English handoff template to skills/digital-state/references/
- [ ] 065 Create .github/ISSUE_TEMPLATE for bug reports and feature requests
- [ ] 066 Add CODE_OF_CONDUCT.md referencing Advisory Standard
- [ ] 067 Create CONTRIBUTING.md for development workflow
- [ ] 068 Verify all governance files can be updated via Builder→Auditor→version bump cycle

## Phase 9: Quality Assurance (Tasks 069-078)

- [ ] 069 Run full test cycle: create parent card → builder evidence → auditor review → implementation → auditor approval
- [ ] 070 Test Evidence Gate: attempt to route to auditor without raw logs (should be blocked)
- [ ] 071 Test Implementation Gate: attempt unauthorized file edit (should be blocked)
- [ ] 072 Test Audit Gate: attempt to close parent without auditor approval (should be blocked)
- [ ] 073 Test Risk Gate: trigger risk, verify risk-ledger entry required before proceeding
- [ ] 074 Test Concurrency Cap: attempt to start second task on same profile (should be blocked)
- [ ] 075 Test Profile Isolation: verify generic delegate_task cannot replace builder/auditor in governed work
- [ ] 076 Test Kanban as Execution Ledger: verify all decisions recorded in kanban.db
- [ ] 077 Test Spec-Kit as Requirements Layer: verify no product-specific reqs in framework files
- [ ] 078 Final validation: run .\scripts\validate-final.ps1 → .\scripts\install.ps1 → end-to-end governance cycle

## Completion Criteria

- [ ] All 78 tasks completed and verified
- [ ] Version 3.1.7 released with signed CHANGELOG.md entry
- [ ] Clean install works on fresh Hermes Agent 0.14.0+
- [ ] End-to-end governance cycle passes all gates
- [ ] No role separation violations in automated tests