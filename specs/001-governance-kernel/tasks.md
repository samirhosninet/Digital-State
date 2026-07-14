# Tasks: Governance Kernel

**Input**: Design documents from `/specs/001-governance-kernel/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included to verify engine correctness and lifecycle compliance.

**Organization**: Tasks are grouped by phase and user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
* **[P]**: Can run in parallel (different files, no dependencies)
* **[Story]**: Which user story this task belongs to (US1, US2, US3)
* All tasks include exact file paths in their descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Create project directories at src/governance and tests/unit/ and tests/integration/
- [x] T002 Initialize project configuration at pyproject.toml
- [x] T003 [P] Configure flake8, black, and pytest formatting rules at pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Implement append-only log writing and integrity verification logic in src/governance/audit.py
- [x] T005 [P] Define core exceptions and domain-specific errors in src/governance/exceptions.py
- [x] T006 Implement configuration and identity loading utility in src/governance/config.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Goal Definition and Verification Gate (Priority: P1) 🎯 MVP

**Goal**: Enable Prime agent to define specification requirements and sign off, transitioning state to PLANNING.

**Independent Test**: Verify that Prime can submit and sign requirements, shifting status to PLANNING, and that unauthorized agents are blocked.

### Tests for User Story 1
- [x] T007 [P] [US1] Create unit tests for AgentRegistry and LifecycleState transitions in tests/unit/test_registry.py
- [x] T008 [P] [US1] Create integration tests verifying goal definition gate transitions in tests/integration/test_story1.py

### Implementation for User Story 1
- [x] T009 [P] [US1] Implement AgentRegistry and role verification in src/governance/registry.py
- [x] T010 [US1] Implement LifecycleState transition logic and SPECIFICATION gate checks in src/governance/engine.py

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Technical Planning & Audit Validation (Priority: P2)

**Goal**: Enable Builder to design and submit a plan, and Auditor to approve or reject, transitioning state to IMPLEMENTATION.

**Independent Test**: Verify Builder can submit plans, status is Pending Audit, and Auditor can approve/reject, shifting status to IMPLEMENTATION.

### Tests for User Story 2
- [x] T011 [P] [US2] Create unit tests for plan submission and auditing gates in tests/unit/test_planning.py
- [x] T012 [P] [US2] Create integration tests verifying plan validation gate in tests/integration/test_story2.py

### Implementation for User Story 2
- [x] T013 [P] [US2] Create VerifiableEvidence data representation in src/governance/models.py
- [x] T014 [US2] Implement PLANNING gate validation rules and Auditor veto logic in src/governance/engine.py

**Checkpoint**: User Stories 1 and 2 work together independently.

---

## Phase 5: User Story 3 - Independent Task Execution & Evidence Audit (Priority: P3)

**Goal**: Enable Auditor to review implementation logs, approve progression, and Prime to accept and complete.

**Independent Test**: Verify Builder can submit implementation evidence logs, Auditor can approve, and Prime can approve final verification, shifting status to COMPLETED.

### Tests for User Story 3
- [x] T015 [P] [US3] Create unit tests for evidence verification and final approval gates in tests/unit/test_verification.py
- [x] T016 [P] [US3] Create integration tests for CLI command flows in tests/integration/test_cli_flow.py

### Implementation for User Story 3
- [x] T017 [US3] Implement IMPLEMENTATION and VERIFICATION gate checks in src/governance/engine.py
- [x] T018 [US3] Implement CLI command parser and contract endpoints in src/governance/cli.py
- [x] T019 [US3] Implement CLI main entry mapping calls to the engine in src/main.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalization and documentation.

- [x] T020 [P] Create project documentation in README.md
- [x] T021 Run all test suites using pytest and validate quickstart.md validation scenario

---

## Dependencies & Execution Order

### Phase Dependencies
* **Setup (Phase 1)**: No dependencies.
* **Foundational (Phase 2)**: Depends on Phase 1. Blocks Phase 3+.
* **User Stories (Phases 3-5)**: Depend on Phase 2 completion. Can proceed sequentially.
* **Polish (Phase 6)**: Depends on all user story completions.

### Parallel Opportunities
* T003, T005, T007, T008, T011, T012, T013, T015, T016, and T020 can be executed in parallel since they reside in separate files with no code dependencies.

---

## Parallel Example: User Story 1
```bash
# Run unit and integration tests for User Story 1 in parallel
pytest tests/unit/test_registry.py
pytest tests/integration/test_story1.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Setup (Phase 1)
2. Complete Foundational (Phase 2)
3. Complete User Story 1 (Phase 3)
4. Validate User Story 1 independently.

### Incremental Delivery
1. Deliver core setup + foundation.
2. Deliver User Story 1 (Requirements gate validation).
3. Deliver User Story 2 (Planning gate validation).
4. Deliver User Story 3 (Execution gate validation and CLI).
5. Deliver Polish and README.
