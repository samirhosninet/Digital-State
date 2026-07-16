# Tasks: Production Trust Hardening

**Input**: Design documents from `specs/009-production-trust-hardening/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

## Phase 1: Setup

- [ ] T001 Document the production trust boundary and migration notice in README.md and SECURITY.md
- [ ] T002 Add release-evidence and recovery snapshot ignore patterns to .gitignore
- [ ] T003 Create reusable cryptographic test-key fixtures in tests/conftest.py

## Phase 2: Foundational Security and Integrity

- [X] T004 Add strict supported public-key metadata validation and key fingerprinting in src/digital_state/core/verifier.py
- [X] T005 Replace plaintext default registrations with explicit cryptographic identity requirements in src/digital_state/core/registry.py
- [X] T006 Reject legacy plaintext verification and return actionable migration errors in src/digital_state/core/evidence.py
- [ ] T007 Record allow/deny authorization decisions and actor provenance in src/digital_state/core/engine.py
- [ ] T008 Fail closed on malformed lifecycle state and verify lifecycle-state/audit consistency in src/digital_state/core/lifecycle.py and src/digital_state/core/audit.py
- [ ] T009 Add preserved-source validation and explicit recovery orchestration in src/digital_state/core/recovery.py

## Phase 3: User Story 1 - Trust a Production Governance Decision (P1)

**Goal**: Only valid cryptographic identities can produce independently authorized governance decisions.

**Independent Test**: Valid ECDSA evidence succeeds; legacy, altered, revoked, role-incorrect, and self-approval requests fail without mutation.

- [ ] T010 [P] [US1] Add invalid-key, revoked-key, and forged-evidence tests in tests/unit/test_cryptography.py
- [ ] T011 [P] [US1] Add self-approval and denied-decision audit tests in tests/unit/test_kernel.py
- [ ] T012 [US1] Enforce signer identity, status, role, and independent approver provenance in src/digital_state/core/engine.py
- [X] T013 [US1] Require cryptographic registration metadata and safe public CLI input handling in src/digital_state/cli/cli.py
- [ ] T014 [US1] Remove legacy signing fixtures and migrate governance journey tests in tests/integration/test_governance_flow.py

## Phase 4: User Story 2 - Know the Real Runtime Boundary (P1)

**Goal**: Diagnostics and hooks distinguish unavailable, simulated, incompatible, and live-verified Hermes states.

**Independent Test**: Fake or absent binaries never produce a live-verified status; only an attested compatible handshake can do so.

- [ ] T015 [P] [US2] Add runtime-mode matrix tests in tests/unit/test_sdk.py and tests/unit/test_plugin.py
- [ ] T016 [US2] Implement runtime attestation, compatibility checks, and explicit mode classification in integrations/hermes/client.py
- [ ] T017 [US2] Surface attestation in doctor output and deny unsupported runtime claims in src/digital_state/cli/cli.py
- [X] T018 [US2] Remove fixed feature fallbacks and bind hook context to validated feature and identity values in src/digital_state/hermes/plugin.py
- [ ] T019 [US2] Validate public runtime classification scenarios in tests/integration/test_hermes_flow.py

## Phase 5: User Story 3 - Investigate Tampering and Recover Safely (P2)

**Goal**: Integrity failures stop mutations and recovery is explicit, validated, preserved, and audited.

**Independent Test**: Tampering fails closed; invalid recovery input causes no mutation; valid recovery preserves originals and produces traceable evidence.

- [ ] T020 [P] [US3] Add tampered-state, log-state mismatch, and stale-lock recovery tests in tests/unit/test_integrity.py and tests/unit/test_recovery.py
- [ ] T021 [US3] Integrate recovery source/confirmation options and structured output into src/digital_state/cli/cli.py
- [ ] T022 [US3] Add recovery event and snapshot checks to src/digital_state/core/audit.py and src/digital_state/core/recovery.py
- [ ] T023 [US3] Validate recovery through the public CLI in tests/integration/test_cli_flow.py

## Phase 6: User Story 4 - Release Only What Was Actually Validated (P2)

**Goal**: A release decision is generated from a clean-environment execution bundle, not a static claim.

**Independent Test**: The release gate rejects dirty/secrets/failing checks and passes only when every public journey executes successfully.

- [ ] T024 [P] [US4] Add dirty-tree, secret-like material, and missing-evidence release-gate tests in tests/integration/test_release_gate.py
- [ ] T025 [US4] Implement JSON release evidence bundle and fail-closed release gate in scripts/release_gate.py
- [ ] T026 [US4] Execute public install, init, doctor, upgrade, uninstall, and recovery journeys from a fresh environment in tests/integration/test_installation.py
- [ ] T027 [US4] Replace static readiness claims with generated release-gate instructions in README.md, RELEASE_READINESS_REPORT.md, and FINAL_RELEASE_GATE_REPORT.md

## Phase 7: Polish and Cross-Cutting Validation

- [ ] T028 Run the complete test suite and record results in specs/009-production-trust-hardening/validation.md
- [ ] T029 Verify no source code or documentation claims local audit storage is immutable in README.md, SECURITY.md, and specs/009-production-trust-hardening/
- [ ] T030 Re-run the pre-mortem findings against the completed implementation and append remaining gaps using SpecKit convergence in specs/009-production-trust-hardening/tasks.md

## Dependencies & Execution Order

`T001–T009` → `US1` and `US2` → `US3` → `US4` → `T028–T030`.

US1 and US2 can proceed together after Phase 2. US3 depends on integrity behavior from Phase 2. US4 depends on finalized public commands and documentation.

## Parallel Opportunities

- T010 and T011 can be implemented in parallel.
- T015 can run alongside the foundational runtime implementation once the contract is settled.
- T020 can run alongside CLI recovery wiring.
- T024 can run alongside release-gate implementation.

## Implementation Strategy

Deliver the security boundary first: no plaintext identity and no self-approval. Then make runtime truthfulness explicit, protect recovery, and finally gate release on reproducible evidence. No release declaration is permitted before Phase 7 passes.
