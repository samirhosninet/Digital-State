# Tasks: Production Hardening

This document defines the actionable, dependency-ordered tasks for the **Production Hardening** governance event.

---

## Phase 1: Setup

- [x] T022 Configure standard cryptography package dependencies in `pyproject.toml`

---

## Phase 2: Foundational

- [x] T023 Implement algorithm-agnostic `CryptoVerifier` interface and ECDSA P-256 validation provider in `src/governance/verifier.py`
- [x] T024 Implement exclusive file-locking manager supporting PID tracking, retries (100ms), and timeout (5s) in `src/governance/locking.py`

---

## Phase 3: User Story 1 - Production Cryptographic Signatures (Priority: P1)

Goal: Implement ECDSA signature verification for all evidence submissions.

- [x] T025 [P] [US1] Create unit tests verifying signature success, modified payloads, malformed PEMs, and disabled keys in `tests/unit/test_cryptography.py`
- [x] T026 [US1] Refactor `Evidence` to delegate validation to `CryptoVerifier` and update registry parser to load key metadata in `src/governance/evidence.py` and `src/governance/registry.py`

---

## Phase 4: User Story 2 - Transactional Persistence & Locking (Priority: P1)

Goal: Implement atomic persistence and exclusive directory-level file locking.

- [x] T027 [P] [US2] Create integration tests verifying concurrency blocks, retry timing, and stress tests in `tests/integration/test_concurrency.py`
- [x] T028 [US2] Implement atomic file commit updates (write to tmp -> fsync -> rename) in `src/governance/lifecycle.py` and `src/governance/audit.py`
- [x] T029 [US2] Wrap kernel write-transition entrypoints with transaction lock manager in `src/governance/engine.py`

---

## Phase 5: User Story 3 - Crash Consistency & Recovery (Priority: P2)

Goal: Implement startup alignment verification.

- [x] T030 [P] [US3] Create unit tests verifying boot alignment checks and recovery from truncated state files in `tests/unit/test_recovery.py`
- [x] T031 [US3] Implement bootstrap state-to-log alignment checks and stale lock cleanup on boot in `src/governance/bootstrap.py` and `src/governance/engine.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T032 Document lock configurations, cryptographic standards, and crash-recovery procedures in `README.md`
