# Tasks: Release Readiness Hardening

**Input**: Design documents from `/specs/004-release-readiness/`

## Phase 1: Setup
- [x] T001 Verify SpecKit workspace exists and loaded governance rules in `.specify/`

## Phase 2: Foundational (T1 - Auditor Review)
**Goal:** Verify architecture, documentation, and user installation journeys.
- [x] T002 [P] Verify `README.md` contains Path A (GitHub Package Install) and Path B (Local Repo Install) descriptions
- [x] T003 [P] Verify dynamic path resolutions in `tests/integration/test_hermes_flow.py`
- [x] T004 [P] Verify dynamic path resolutions in `tests/integration/test_installation.py`

## Phase 3: Sanitizer Review (T2)
**Goal:** Scan for local paths, credentials, and clean up temporary leftovers.
- [x] T005 [P] Audit `agents.json` to ensure only empty schemas exist with no committed private credentials
- [x] T006 [P] Verify gitignore rules ignore local machine artifacts and virtualenvs

## Phase 4: Debugger Validation (T3)
**Goal:** Validate CLI robustness and error handling.
- [x] T007 [P] [US3] Verify `digitalstate init` idempotency and non-destructive behaviors
- [x] T008 [P] [US3] Verify `digitalstate doctor` diagnostic outputs when missing config directories

## Phase 5: Security Review (T4)
**Goal:** Dependency safety and cryptographic boundaries.
- [x] T009 [P] [US4] Audit core dependency boundaries in `pyproject.toml`
- [x] T010 [P] [US4] Audit ECDSA signature check constraints in `src/digital_state/sdk/api.py`

## Phase 6: Final Release Gate (T5)
**Goal:** Produce release readiness documentation and sign off.
- [x] T011 [US5] Generate the final `RELEASE_READINESS_REPORT.md`
