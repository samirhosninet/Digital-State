# Tasks: Hermes Runtime Integration

**Input**: Design documents from `/specs/003-hermes-runtime-integration/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as requested by the governance specification to verify full runtime coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/`, `tests/` at repository root
- Paths match the namespace: `src/digital_state/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize specs and checklists structure for 003-hermes-runtime-integration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Configure Python test environment for execution of integration tests in pyproject.toml

---

## Phase 3: User Story 1 - Plugin Handshake & Loading (Priority: P1) 🎯 MVP

**Goal**: Load the plugin and run the compatibility check on startup.

**Independent Test**: Verify version mismatch blocks initialization and logs a version mismatch alert.

### Tests for User Story 1
- [x] T003 [P] [US1] Create unit test for version handshake and mismatch logic in tests/unit/test_plugin.py

### Implementation for User Story 1
- [x] T004 [US1] Implement compatibility check and version mismatch event logging in src/digital_state/hermes/plugin.py

---

## Phase 4: User Story 2 - Lifecycle Hook Interception (Priority: P1)

**Goal**: Register all lifecycle hooks and intercept events with Fail-Safe Deny logic.

**Independent Test**: Run simulated session flows and assert all hooks execute.

### Tests for User Story 2
- [x] T005 [P] [US2] Create unit tests for hook handlers in tests/unit/test_plugin.py
- [x] T006 [P] [US2] Create integration test for full session loop in tests/integration/test_hermes_flow.py

### Implementation for User Story 2
- [x] T007 [US2] Update src/digital_state/hermes/plugin.py to register all 6 hooks and implement handlers
- [x] T008 [US2] Refactor mock client in integrations/hermes/client.py to simulate the plugin lifecycle run loop

---

## Phase 5: User Story 3 - Command Routing (Priority: P2)

**Goal**: Support slash commands /approve and /veto and route them to the SDK.

**Independent Test**: Invoke slash command handlers and assert correct routing.

### Implementation for User Story 3
- [x] T009 [US3] Implement slash command routing for /approve and /veto in src/digital_state/hermes/plugin.py

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and documentation.

- [x] T010 [P] Update documentation files specs/ARCHITECTURE.md and README.md with the integration results
- [x] T011 Run quickstart.md validation commands to verify the local integration test suite
- [x] T012 Verify clean git status and push changes to remote main branch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) must complete before User Story 2 (P1)
  - User Story 2 (P1) must complete before User Story 3 (P2)
- **Polish (Final Phase)**: Depends on all user stories being complete

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready
