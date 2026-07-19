# Tasks: Multi-Tenant Key Server Authentication

**Input**: Design documents from `/specs/011-multi-tenant-key-server/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Initialize spec and checklist directory structure for 011-multi-tenant-key-server

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 Update `RuntimeStore` schema in `src/digital_state/runtime/store.py` to support optional `tenant_id` scoping in identity queries

---

## Phase 3: User Story 1 - Authenticate Multi-Tenant Key Server Requests (Priority: P1)

**Goal**: Extend governance context adapter to extract and validate `tenant_id` across all 3 resolution tiers.

- [x] T003 [P] [US1] Create unit tests for tenant-scoped context resolution in `tests/unit/test_adapter.py`
- [x] T004 [US1] Update `resolve_governance_context` in `src/digital_state/runtime/adapter.py` to extract `tenant_id` from dict, environment, and workspace state
- [x] T005 [US1] Update `DigitalStatePlugin._governed_context` in `src/digital_state/hermes/plugin.py` to pass tenant-aware context

---

## Phase 4: User Story 2 - Register and Provision Tenant Cryptographic Identities (Priority: P1)

**Goal**: Support tenant-scoped identity provisioning in `RuntimeStore`.

- [x] T006 [P] [US2] Create integration tests for multi-tenant key provisioning in `tests/integration/test_tenant_isolation.py`
- [x] T007 [US2] Update identity registration logic in `src/digital_state/core/registry.py` to enforce tenant identity scoping

---

## Phase 5: User Story 3 - Single-Tenant Backward Compatibility (Priority: P2)

**Goal**: Guarantee fallback to `default_tenant` for un-scoped requests.

- [x] T008 [P] [US3] Verify backward compatibility test suite in `tests/unit/test_plugin.py` with un-scoped single-tenant requests

---

## Phase 6: Polish & Verification

- [x] T009 Run `python scripts/verify_hook_contract.py` to confirm hard enforcement
- [x] T010 Run `pytest tests/` to confirm zero regressions
- [x] T011 Run `python -m digital_state.cli.cli doctor` to confirm system health

