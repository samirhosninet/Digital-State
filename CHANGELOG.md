---
version: 3.3.0
updated: 2026-06-24
compatibility: hermes-agent>=0.14.0
---

# Changelog
All notable changes to the Digital State final package are documented here.

## [3.3.0] - 2026-06-24

### Added
- **Phase 10: Hardening & Release** — 9 new tasks (T079–T087) closing risks, adding tests, and removing portability violations
- `scripts/uninstall.ps1` — full uninstaller with profile/skill/plugin removal and backup discovery (T082)
- `scripts/promote-to-review.sh` — CLI wrapper for the canonical `blocked → review` DB promotion (T080, RISK-001 mitigation)
- `tests/` pytest suite: `test_version_sync.py`, `test_concurrency_cap.py`, `test_risk_ledger.py`, `test_validate_final.py` (T083)
- `scripts/uninstall.ps1`, `scripts/promote-to-review.sh`, `tests/` added to `distribution_owned` (T085)
- Phase 10 documented in `specs/plan.md` and `specs/tasks.md` (T079–T087)

### Changed
- **Removed model/provider from all profile `config.yaml` files** — portable overlay: `config.yaml` now contains only `kanban:` and `toolsets:`; model config is an installer concern (T081, RISK-006)
- `risk-ledger.md` — RISK-001 status: Open → Mitigated (promote-to-review.sh created); RISK-002 status: Open → Closed (install.ps1 `.Trim` fix verified)
- `specs/plan.md` — added Phase 10: Hardening & Release with Rationale and Constraints
- `specs/tasks.md` — added 9 new tasks (T079–T087), updated Completion Criteria
- `distribution.yaml` — version 3.2.0 → 3.3.0; added new files to `distribution_owned`
- All profile `SOUL.md` frontmatter: version 3.2.0 → 3.3.0
- `README.md`, `PACKAGE.md`, `specs/plan.md`, `specs/tasks.md`: version references 3.2.0 → 3.3.0

### Removed
- `model:` and `provider:` blocks from `profiles/*/config.yaml` — these now belong to the installer/operator, not the portable package

### Security
- RISK-001 closed: `promote-to-review.sh` provides a canonical CLI path for the `blocked → review` DB promotion
- RISK-002 closed: `install.ps1` line 60 quoting fix (`.Trim([char]34, [char]39)`) verified
- RISK-006 addressed: no model/provider in portable config → eliminates model lock-in risk at package level

### Added
- `CONTRIBUTING.md` — governance contribution guide
- `CODE_OF_CONDUCT.md` — community standards
- `.github/ISSUE_TEMPLATE/` — bug_report.md, feature_request.md with Evidence Gate

### Changed
- **Unified all version strings to 3.2.0** across distribution.yaml, README.md, PACKAGE.md, CHANGELOG.md, and all three profile SOUL.md files
- `validate-final.ps1` — rewritten with comprehensive checks: concurrency cap, version bump, config.yaml, Arabic template exclusion
- `tasks.md` — all 77 tasks verified and marked complete (100% phase completion)
- Profile toolsets: prime=[kanban,terminal,file], builder=[kanban,terminal,file,web], auditor=[kanban,terminal,file,web,audit-matrix]

### Verified
- **All 5 Gates** tested on Kanban: Evidence, Implementation, Audit, Risk, Concurrency Cap
- **block→review promotion** tested end-to-end on card t_9e644a1d: builder blocks with review-required → Prime promotes to review → dispatcher auto-spawns auditor
- **Full governance cycle** tested: create parent → builder evidence → auditor review → implementation → auditor approval
- **Clean install** verified: all 3 profiles installed with correct toolsets + concurrency cap + 3 baseline skills
- **Install backups** verified: 35+ backup timestamps with all profiles

## [3.1.7] - 2026-06-23

### Added
- Profile `config.yaml` files for all three profiles (`prime`, `builder`, `auditor`) with:
  - `kanban.max_in_progress_per_profile: 1` (Constitution Article XIII enforcement)
  - Model: `nvidia/nemotron-3-super-120b-a12b`
  - Role-differentiated toolsets: prime (kanban,terminal,file), builder (+web), auditor (+web +audit-matrix)
- `risk-ledger.md`  canonical risk store with 5 initial entries (RISK-001 to RISK-005)
- `scripts/install-simple.ps1`  streamlined installer that works without quoting issues
- `plugins/audit-matrix/` to `distribution_owned` in `distribution.yaml`
- Profile `config.yaml` files to `distribution_owned` in `distribution.yaml`
- `risk-ledger.md` to `distribution_owned` in `distribution.yaml`
- `CODE_OF_CONDUCT.md` referencing Advisory Standard principles with Digital State governance enforcement (T066)
- `CONTRIBUTING.md` with version governance, file boundaries, risk workflow, concurrency rules, commit conventions (T067)
- `skills/premortem-plus/references/fmea-template.md` — FMEA worksheet as markdown with RPN rubric (T044)
- `skills/premortem-plus/references/threat-model.md` — threat modeling worksheet (T043)
- `skills/digital-state/references/handoff-template-ar.md` — Arabic handoff template (T064)
- Concurrency cap validation in `validate-final.ps1` [9/10] check (T053)

### Changed
- `distribution.yaml` version bumped from 3.1.6 to 3.1.7
- `distribution_owned` expanded to include `profiles/*/config.yaml`, `plugins/audit-matrix/`, and `risk-ledger.md`
- `specs/tasks.md` populated with 9-phase / 82-task project plan mapped to Spec-Kit artifacts
- `constitution.md` Article XIV added  native Hermes `review` status adoption
- `validate-final.ps1` upgraded from 9 to 10 checks: added config.yaml concurrency cap, excluded `-ar.md` template files from English-only check, added config.yaml as required files
- `PACKAGE.md` updated from v3.1.0 to v3.1.7 with updated tool policy table, risk-ledger, governance files
- `README.md` added full install.ps1 option in Quick Start
- Profile config.yaml files now role-differentiated: builder adds `web`, auditor adds `web` + `audit-matrix`

### Fixed
- Identified and fixed `install.ps1` `Get-RootModelConfig` line 60 quoting bug (RISK-002 in risk-ledger.md): `.Trim('"', "'")` → `.Trim([char]34, [char]39)`
- `validate-final.ps1` Arabic Unicode false positive on `handoff-template-ar.md` — template files with `-ar.md` suffix now excluded from English-only check
- Documented `blocked → review` promotion gap (RISK-001 in risk-ledger.md)

### Governance
- Constitution Article XIV: Native Hermes `review` status is the canonical Digital State review stage
- Risk Ledger established with 5 risks; RISK-004 accepted, RISK-005 suppressed

## [3.1.6] - 2026-06-21

### Added
- Phase B codification of the **`review-required` block** as the canonical
  Phase B Digital State review handoff, on top of the Phase A evidence
  already collected on parent card `t_279fe5fa`:
  - `AGENTS.md` 3.6.0  3.7.0: new Native-review canonical handoff
    (Phase B) key text in Workflow Stage Mapping; the two table rows
    that used "Ready for Review (same card)" are rewritten to "
    **Blocked (review-required)**" so Builder is the actor that closes
    out the implementation card via the canonical block signal.
    Running  Review transition (canonical Phase B handoff) is
    rewritten to spell out the worker-tool-surface restriction (no
    `kanban_*` worker tool writes `status='review'`) and to make the
    `blocked  review` write responsibility explicit: Prime-direct
    DB write; failing that, operator DB write; failing that, the
    legacy child-Auditor-card fallback. New "Why `review-required`
    block (not `kanban_complete`)" sub-section explains the audit
    consequences of `complete_task  status='done'`.
  - `specs/constitution.md` 1.5.0  1.6.0: Article XIV XIV retitled
    "Native Hermes Review Lifecycle" but the body now spells out
    the `running  review-required (blocked)  review  done/rejected`
    lifecycle, with Prime OR operator owning the blocking-to-review
    promotion step. XIV.1 worker-writeable surface restriction
    extended to acknowledge that not even Prime has a `kanban_*`
    tool to write `status='review'`  Prime's path requires raw DB
    write; otherwise the operator pathway is canonical. New
    sub-section XIV.3 was retitled "Canonical handoff vs child-card
    rule" and the bullet phrasing disambiguates Prime-or-operator
    from a hypothetical Prime-callable tool. Global Forbidden
    Actions gains a new bullet pinning canonical capitalization:
    lowercase `review-required:` only, not `REVIEW_REQUIRED:`.
  - `profiles/prime/SOUL.md` 3.2.0  3.3.0: Identity rewritten to
    state the canonical handoff is Builder's `review-required`
    block, not Prime's tool call. Protocol step 6 (Native-review
    promotion) replaces the prior "Native-review transition check"
    with a three-tier detection (Prime-direct-write; operator
    handoff; child-card fallback). Routing Table row for Builder
    `reason="review-required:"` clarifies that the route is a
    promotion, not a transaction. Boundaries section replaces
    "skip the canonical native-review **transaction**" with "skip
    the canonical native-review **promotion**".
  - `profiles/builder/SOUL.md` 3.2.0  3.3.0: Identity rewritten
    so the implementation-card handoff is unambiguously
    `kanban_block(reason="review-required: ...")` and not
    `kanban_complete()`. Protocol step 9 (Native review handoff)
    uses lowercase `review-required:` throughout and clarifies
    that the actual promotion is Prime/operator responsibility.
    New Boundaries entry pins canonical capitalization:
    lowercase `review-required:` only, not `REVIEW_REQUIRED:`.
  - `profiles/auditor/SOUL.md` 3.2.0  3.3.0: Identity spells out
    that the Auditor is auto-spawned on the same card after the
    Prime/operator promotion from `blocked  review`.
- Documentation reinforcement of the AGENTS.md single-source
  reference from `AGENTS.md Running  Review transition` and
  `specs/constitution.md` Article XIV  the prior v3.2.0 changelog
  entries on each SOUL.md remain in place as historic record of the
  v3.2.0 native-review adoption, and the new v3.3.0 entry on each
  SOUL.md is the authoritative codification that supersedes them.

### Fixed
- Phase A finding corrected Phase B misframings: the v3.2.0 narrative
  in AGENTS.md, constitution.md, and the three SOUL.md files
  consistently described the `running/blocked  review` write as "
  Prime-callable", which Phase A evidence on `t_279fe5fa`
  (and now Phase B evidence on `t_fbcf9e45`) confirms is **not**
  true in the current Hermes dispatcher's worker surface. The
  Prometheus-rule governance text now says "Prime or operator"
  throughout. The legacy child-Auditor-card workflow is now
  explicitly a fallback, never the canonical default.

### Authorization
- Kanban card `t_fbcf9e45` (Phase B supersedes `t_279fe5fa`,
  parent `t_29c28516`) records Phase B IMPLEMENT authorization
  with the user's directive: codify the `review-required` block as
  the canonical Digital State review handoff. File boundaries named
  in the card body: `AGENTS.md`, `specs/constitution.md`,
  `profiles/prime/SOUL.md`, `profiles/builder/SOUL.md`,
  `profiles/auditor/SOUL.md`, `CHANGELOG.md`. Constitution
  compliance verified per Articles I (durable governance directive,
  with this CHANGELOG entry as the recording), VIII (version bump +
  CHANGELOG entry), and XIV (canonical Phase B handoff).

### Notes
- No new skills, scripts, or directories were created; no
  files outside the six authorized were modified; no Hermes
  source, `.env`, profile secret, target-project path, or
  product-specific requirement has been hardcoded into any
  reusable Digital State framework file.

## [3.1.5] - 2026-06-21

### Changed
- **Config-only rate/concurrency guard (correction).** Premortem-rejection
  cleaned up the stale governance references that pointed at a
  separate reusable skill for the rate-limit / concurrency rule.
  There is no such skill and no script/wrapper  the rule is
  config-only.
- Active profiles (`prime`, `builder`, `auditor`) now carry:
  - `model.max_requests_per_minute: 20` (rate-limit guard).
  - `kanban.max_in_progress_per_profile: 1` (concurrency guard).
  - `prime` previously had `kanban.max_in_progress_per_profile` absent
    and now has it set; `builder` and `auditor` were already correct.
- `AGENTS.md` 3.5.0  3.5.1: removed the bullet pointing at the missing
  reusable skill in the references list and updated the Concurrency
  Cap Gate paragraph so the source of truth is the profile-config key
  itself; added an explicit **Rate-limit guard (config-only)**
  paragraph for the `model.max_requests_per_minute` key.
- `specs/constitution.md` 1.4.0  1.4.1: replaced the bullet that
  pointed at the reusable skill with a **Config-only rule** bullet
  stating that `model.max_requests_per_minute` and
  `kanban.max_in_progress_per_profile` are the single source of
  truth; updated the Article XIII binding-guarantee enumeration to
  drop the skill reference.
- `profiles/prime/SOUL.md` 3.1.1  3.1.2.
- `profiles/builder/SOUL.md` 3.1.1  3.1.2.
- `profiles/auditor/SOUL.md` 3.1.1  3.1.2.

### Fixed
- Stale governance references that implied a required reusable skill
  for rate-limit / concurrency enforcement are removed from all active
  governance surfaces. No such skill, script, or wrapper existed on
  disk; none has been or will be created.
- Three residual narrative references to the legacy "rate limit guard"
  term inside the v3.1.1 changelog entries of `profiles/prime/SOUL.md`,
  `profiles/builder/SOUL.md`, and `profiles/auditor/SOUL.md` were
  rewritten to refer to the rule by its current name (**Concurrency
  Cap Gate** / config-only) and annotated with a note explaining that
  the legacy name was deprecated at v3.1.2. This brings the legacy-name
  search to a clean exit (no hyphenated form hits remain in any of the
  six governance files: `AGENTS.md`, `specs/constitution.md`, the three
  `profiles/<role>/SOUL.md` files, and `CHANGELOG.md`).

### Authorization
- User authorization: this correction was driven by a user directive
  recorded on the parent Kanban card: "rate/concurrency guard is
  config-only, not a reusable skill" (Arabic:  / `authorized`).
  File boundaries named in the card body: `AGENTS.md`,
  `specs/constitution.md`, three `profiles/<role>/SOUL.md` files,
  `CHANGELOG.md`, plus the active `~/.hermes/profiles/<role>/config.yaml`
  keys via the `hermes -p <role> config set` CLI commands explicitly
  enumerated in the card. Constitution compliance verified per
  Articles I (durable governance directive, with this CHANGELOG
  entry as the recording), VIII (version bump + CHANGELOG entry),
  and Article XIII (binding installation guarantee is enforced by
  installer/validator/SOUL.md Protocol, not by an external skill).

## [3.1.4] - 2026-06-21

### Added
- Durably recorded the user / project owner's architectural directive
  ("an architectural directive must be recorded in project files so it
  does not remain an assistant decision but becomes foundational
  architecture") as a non-negotiable durable governance rule:
  - `specs/constitution.md` Article I  **Durable Governance Directives
    (NON-NEGOTIABLE)**: full rule text, verbatim source note pointing
    back at the original Arabic/English directive, recording-required
    list (`specs/constitution.md`, `AGENTS.md`, optionally
    `specs/tasks.md`), and the explicit principle that a chat-only
    directive is a transient decision, not architecture.
  - `AGENTS.md` Durable Governance Directives: agent-facing operating
    rule that binds every agent (including the current-session
    assistant) and is enforced by Prime before any implementation
    child task is dispatched. Source note preserves the verbatim user
    requirement. Cross-references Constitution Article I.
  - `specs/spec.md` Current Project Mission line 25: parallel
    one-line reinforcement that durable architecture requires
    recording under `AGENTS.md` Durable Governance Directives and
    the relevant Spec-Kit artifact (Constitution Article I).
  - Added an explicit Global Forbidden Actions bullet in `AGENTS.md`
    matching Article I ("Treat a chat-only architectural/governance
    directive as durable architecture without recording it under the
    Durable Governance Directives section above (Constitution
    Article I)") so the rule is enforceable from both files.
- Reinforced the routing rule in `AGENTS.md` Workflow Stage
  Transitions / Gate Enforcement section and in the Profile Isolation
  Boundary block: actual file changes MUST flow Builder  Auditor,
  generic `delegate_task` subagents MUST NOT be substituted for
  these profiles in governed work (Constitution Article III).

### Changed
- `specs/constitution.md` frontmatter advanced 1.2.0  1.3.0:
  records Article I (Durable Governance Directives), Article XII
  placeholder, Mission paragraph reinforcement, and the Governance
  section cross-references.
- `AGENTS.md` frontmatter advanced 3.3.0  3.4.0: records the new
  Durable Governance Directives section, the Framework Scope
  cleanup, the Specification-Kit mission citation in Current Project
  Mission, and the new Global Forbidden Actions bullet.

### Authorization
- Kanban card `t_7c55e645` (Prime  Builder IMPLEMENT) records the
  user / project owner's verbatim directive (Arabic) that
  architectural / governance instructions be recorded in project
  files / Spec-Kit governance "so it does not remain an
  assistant decision, but becomes foundational architecture".
  File boundaries named in the card body: `specs/constitution.md`,
  `AGENTS.md`, optionally `specs/tasks.md`. Constitution compliance
  verified per Article I (durable governance directive), Article III
  (Profile Isolation Boundary / Builder-Auditor routing), Article
  VIII (version bump + CHANGELOG entry), and Article XI (no
  target-project paths, card IDs, or product state carried into
  reusable framework files).

### Notes
- `specs/tasks.md` is still the unmodified Spec-Kit **template**
  (placeholder `[FEATURE NAME]` and the T001/T002 illustrative
  scaffold) on purpose: Constitution Article I treats the
  `tasks.md` recording as OPTIONAL ("may include the rule" only
  "when relevant"). Adding the rule to a still-template file
  would create a one-off governance-injection fragment outside
  the proper Spec-Kit task-generation flow that replaces template
  scaffolding with real user-story tasks per `specs/spec.md`.
  The rule remains durably enforced via constitution Article I and
  AGENTS.md Durable Governance Directives, both of which already
  cite the `tasks.md` recording path for cases where a real
  Spec-Kit task list later exists.
- No Hermes source, `.env`, profile secret, target-project path,
  card ID from a prior run, or product-specific requirement has
  been hardcoded into any reusable Digital State framework file.
  All cross-references in the new governance text match the
  canonical statements in Constitution Articles I and III.

## [3.1.3] - 2026-06-20

### Added
- Constitution Article XI  Universal Reusable Overlay Scope (NON-NEGOTIABLE):
  asserts Digital State is a universal reusable governance overlay
  installable on any target (public, private, vendor-delivered,
  monorepo, single-repo, regulated, arbitrary). Hard-codes the rule
  that reusable framework files (`AGENTS.md`, `SOUL.md`, governance
  skills, baseline contracts, installer/validator logic, distribution
  manifest) MUST NOT carry target-project paths, Hermes Kanban card
  IDs, repository names, branches, migration state, model/provider
  choices, or product-specific requirements. Records where target
  state belongs instead: target Spec-Kit files for product
  requirements; target Hermes Kanban board for execution/audit.
- Footer updates in `specs/constitution.md`: Governance section now
  cross-references Article XI; Global Forbidden Actions adds an
  explicit hard-coding prohibition; the version footer advances from
  1.0.2  1.1.0.
- New `## Universal Reusable Overlay Scope` section in
  `specs/spec.md` and `specs/plan.md`, with the universal-overlay
  principle, scope statements, boundary test, and an explicit
  compatibility note tying it to the active Self-Development mission
  (Goals A and B).

### Authorization
- Kanban card `t_1a6f1605` (Prime  Builder IMPLEMENT) records the
  user's Arabic clarification:
  "Digital State must later work on any project: public, private, or anything."
  ("Digital State must later work on any project: public, private,
  or anything."). File boundaries named in the card body:
  `specs/constitution.md`, `specs/spec.md`, `specs/plan.md`,
  `AGENTS.md`. Constitution compliance verified per Article VIII
  (version bump + CHANGELOG entry), Article I (durable governance
  directive), and the new Article XI (universal reusable overlay
  scope).

### Notes
- `AGENTS.md` (3.3.0) was already compliant with the universal
  overlay contract via Reusable Overlay Contract, Project-Agnostic
  Operation, Architecture Invariants, and Framework File Hygiene,
  and was therefore not modified in this card. The constitutional
  Article XI is the new single source of truth; `specs/spec.md`
  and `specs/plan.md` now cross-reference Article XI as the binding
  statement.

## [3.1.2] - 2026-06-20

### Added
- `AGENTS.md` 3.2.0  3.3.0: new top-level Current Project Mission section summarizing the active meta-architecture effort (Goals A and B), Spec-Kit/Kanban source-layer rule, mandatory baseline skills, and profile-isolation requirement. Points to the canonical statements in `specs/constitution.md` and `specs/spec.md`.
- `specs/spec.md`: filled the Spec-Kit template header with the project mission (Goal A / Goal B) and added a `## Current Project Mission` section that names Spec-Kit as the requirements/planning source and Kanban as the execution/audit source. Template body retained for downstream user-story detail.
- `specs/plan.md`: filled the Spec-Kit template header with the project branch and date, and added a `## Current Project Mission / Self-Development Scope` section binding the plan to Kanban-execution routing, Constitution gates, and profile isolation. Template body retained.

### Authorization
- Kanban card `t_77765ade` (Prime  Builder IMPLEMENT) records the user's Arabic clarification about the active meta-architecture effort. File boundaries named in the card body: `specs/constitution.md`, `specs/spec.md`, `specs/plan.md`, `AGENTS.md` only. Constitution compliance verified per Article VIII (version bump + CHANGELOG entry) and Article I (durable governance directive).

### Notes
- `specs/constitution.md` was already compliant (contained Current Project Mission at lines 1528 with the canonical mission statement) and was therefore not modified in this card. The constitutional mission statement remains the single source of truth; AGENTS.md and specs/spec.md cross-reference it.

## [3.1.1] - 2026-06-20

### Added
- Constitution Article X: Kanban concurrency cap is mandatory durable architecture. `kanban.max_in_progress_per_profile = 1` must hold for every Digital State profile.
- Installer/validator enforcement hook: validator MUST fail if `kanban.max_in_progress_per_profile` is missing, `null`, or != 1 in any profile config (enforcement tracked under follow-up card).

### Fixed
- Prime profile config (`profiles/prime/config.yaml`): `kanban.max_in_progress_per_profile` raised from `null` to `1` to prevent provider rate limits and to enforce sequential evidence/audit flow.

### Changed
- `AGENTS.md` 3.1.2  3.1.3: added runtime cross-reference to Constitution Article X.
- `specs/constitution.md` 1.0.1  1.0.2: new Article X, updated Governance section, added YAML-style metadata block at file head (version/updated/compatibility).

### Authorization
- User directive (Arabic) recorded on Kanban card `t_d7dacae0`: "It should be one card after it finishes to avoid the RATE LIMIT". Card body authorizes Builder IMPLEMENT on Prime config.yaml + governance/spec files per published file boundaries.

## [3.1.0] - 2026-06-20

### Refactored
- Extracted Advisory Standard into `skills/advisory-standard/SKILL.md` (single source of truth)
- Removed Advisory Standard prose duplication from all 3 SOUL.md files
- Deduplicated AGENTS.md: tool permission matrix, workflow stage table, and legacy role mapping now reference `skills/digital-state/SKILL.md`
- Removed threat model and kill criteria duplication from `skills/digital-state/SKILL.md`; references `skills/premortem-plus/SKILL.md`
- Fixed dead references in SKILL.md extension patterns (steps 7-8 now reference AGENTS.md and install/validator)
- Moved `install.ps1` and `validate-final.ps1` into `scripts/` subdirectory
- DRY version: both scripts read version from `distribution.yaml` instead of hardcoding
- Added YAML frontmatter to `AGENTS.md`, `README.md`, and `PACKAGE.md`
- Simplified `README.md` to lightweight entry-point; details in `PACKAGE.md`
- Renumbered validator sections (1-9 instead of 1-8+6b)
- Added SKILL.md version validation check
- Added `.gitignore` and `CHANGELOG.md`

### Fixed
- `skills/digital-state/SKILL.md` version 3.0.0  3.1.0 (was out of sync with distribution)

## [3.0.1] - 2026-06-19

### Added
- Shared Advisory Standard in every active profile
- Safe installer with automatic tool policy and model config copy
- Final validator (96 checks)
- English-only enforcement, no Arabic Unicode

## [3.0.0] - 2026-06-03

### Changed
- Breaking: simplified from 5 agents to 3 (prime/builder/auditor)
- Retired analyst, researcher, coder, tester roles
