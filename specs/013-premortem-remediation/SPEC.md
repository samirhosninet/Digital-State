# Specification: PREMORTEM Engineering Remediation (v1.16.0-remediation)

## Feature Overview
- **Feature ID:** `feat-013`
- **Specification Directory:** `specs/013-premortem-remediation`
- **Target Baseline Version:** `v1.16.0-remediation`
- **Certified Baseline Input:** `v1.15.0` (`5950f9d`)
- **Operating Mode:** PLANNING & CLARIFICATION ONLY (Zero code execution / zero commits / zero tags)

---

## 1. Problem Statement
The Digital State repository (`v1.15.0`) has achieved baseline functionality across governance kernel enforcement, device keystore abstractions, multi-tenant evidence federation, and Hermes runtime integration. However, a rigorous PREMORTEM analysis revealed critical engineering vulnerabilities, security weaknesses, architectural gaps, and operational failure risks across six core domains:
1. **Installation & Bootstrap:** Hardcoded installation timestamps, non-atomic bootstrap directory creation lacking transactional rollback, in-place non-atomic Hermes `config.yaml` mutation, and environment path isolation failures.
2. **Device Identity & Cryptography:** Trivial SHA-256 XOR cipher fallback for private key storage on non-Windows/non-DPAPI platforms, pseudo-random hex strings used in place of authentic CA certificate signatures, and complete absence of automated certificate renewal and key revocation protocols.
3. **Evidence Governance:** Attestation bypass in multi-tenant evidence federation when signature fields are omitted, missing OS file locking during audit ledger hash chaining allowing inter-line corruption under high concurrency, and superficial file-existence-only checking in 4-file evidence bundle validation.
4. **Hermes Integration:** Silent governance context fallback when running outside mock contexts, process environment variable trusting for agent profile resolution allowing identity spoofing, and unhandled hook exception masking.
5. **CLI & User Experience:** Non-standard exit code propagation (returning `0` on failures), unhandled input parameter edge cases, and documentation-implementation drift on administrative CLI subcommands (`upgrade`, `uninstall`, `repair`).
6. **Testing & Release Engineering:** Lack of negative cryptographic test coverage, absence of containerized end-to-end integration tests with real Hermes agent binaries, and CI pipeline gaps where evidence auditing (`digitalstate audit-evidence`) is not enforced as a blocking release gate.

---

## 2. Clarified Architectural Decisions (Clarification Pass)

### Architectural Decision 1: Key Management Model
- **Decision:** Hybrid 2-Tier OS-Keyring & Headless PBKDF2 AES-256-GCM Storage Model.
- **Specification:**
  - *Tier 1 (Desktop OS):* Windows DPAPI via `win32crypt`, macOS Keychain API, or Linux SecretService API via `keyring`.
  - *Tier 2 (Headless / Container):* FIPS-compliant AES-256-GCM encryption with 256-bit key derived via PBKDF2-HMAC-SHA256 (100,000 iterations) using hardware-bound salt (`/etc/machine-id` or system UUID) and optional `DS_MASTER_KEY` environment secret.
  - *Deprecation:* Legacy XOR cipher (`_xor_cipher`) is strictly removed.

### Architectural Decision 2: Certificate Authority Ownership
- **Decision:** Tenant-Isolated Ephemeral Local CA & Central Key Server Dual Model.
- **Specification:**
  - *Local Standalone:* `digitalstate init` provisions an ECDSA P-256 Local CA keypair stored in `.specify/device/ca-key.enc` to cryptographically sign `device-certificate.json`.
  - *Enterprise Multi-Tenant:* Connects to `ADR-011` Key Server, where central CA verifies enrollment challenge nonces and issues signed `device-certificate.json` metadata.
  - *Deprecation:* `secrets.token_hex(64)` pseudo-signatures are strictly eliminated.

### Architectural Decision 3: Hermes Trust Root
- **Decision:** Cryptographically Signed Session Token Trust Root (ADR-013 Refinement E).
- **Specification:**
  - Hermes runtime issues an ephemeral session token payload signed by the workspace kernel key upon session start.
  - `DigitalStatePlugin` verifies token signature against kernel public keys registered in `.specify/memory/agents.json`.
  - *Deprecation:* Un-authenticated process environment variables (`HERMES_PROFILE`) are no longer trusted as identity proof.

### Architectural Decision 4: Offline Enrollment & Grace Period Policy
- **Decision:** 3-State Enforced Grace Period Policy.
- **Specification:**
  - *`< 12 Hours Offline` (ACTIVE):* Full execution allowed using cached CA certificate verification.
  - *`12 to 24 Hours Offline` (WARNING):* Execution allowed; warning appended to audit ledger.
  - *`>= 24 Hours Offline / Expired` (DEFAULT_DENY):* All tool calls blocked (`action: block`) until server sync or admin offline override token (`digitalstate-device override --token <token>`).

### Architectural Decision 5: Federation Attestation Policy
- **Decision:** Strict Fail-Closed Default-Deny Attestation Policy.
- **Specification:**
  - In `FederatedEvidenceManager`, any bundle omitting `public_key_pem`, `challenge_nonce`, or `signature_hex` is marked `is_valid = False`, classified as `UNVERIFIED`, and increments `failed_devices += 1`.
  - Multi-tenant audit checks (`digitalstate audit-evidence --federated`) exit with non-zero code `1` if `failed_devices > 0`.
  - *Deprecation:* "Attestation omitted" bypass (`is_valid = True`) is strictly removed.

---

## 3. Current State
- **Baseline Version:** `v1.15.0` (`5950f9d`).
- **Bootstrap:** `installer.py` writes `"installed_at": "2026-07-20T04:35:00Z"` hardcoded and mutates `config.yaml` directly without `.tmp` replacement.
- **Cryptography:** `keystore.py` falls back to XOR cipher using host hardware metadata string; `enrollment.py` issues `secrets.token_hex(64)` as certificate signatures.
- **Federation:** `manager.py` marks omitted signatures as `is_valid = True` with message `"Attestation omitted."`.
- **Ledger:** `device_ledger.py` and `engine.py` append to `.jsonl` files without OS-level process file locking.
- **CLI:** Error paths print text but exit with return code `0`.
- **CI/CD:** `.github/workflows/evidence-audit.yml` runs unit tests but does not block build artifacts on `audit-evidence --check`.

---

## 4. Target State (v1.16.0-remediation)
- **Zero-Touch Bootstrap:** Fully atomic, idempotent, dynamic ISO-8601 timestamping with transactional rollback cleanup on any step failure, and atomic `.tmp` file replacement for `config.yaml`.
- **FIPS-Compliant Cryptography:** AES-256-GCM / OS Keyring hardware-bound private key storage; true ECDSA P-256 CA-signed device certificates; automated certificate renewal and revocation protocols.
- **Strict Evidence Governance:** Strict Default-Deny attestation enforcement in multi-tenant federation; OS `FileLock` protection on all ledger appends; deep JSON schema and cryptographic signature validation for 4-file evidence bundles.
- **Hardened Hermes Integration:** Cryptographically authenticated session tokens for profile verification; mandatory fail-closed session abort on context resolution failure; structured audit logging for hook exceptions.
- **Standardized CLI & UX:** Strict exit codes (`0` success, `1` governance failure, `2` argument error, `3` I/O error); fully implemented `upgrade`, `uninstall`, and `repair` commands.
- **Comprehensive Testing & CI Gate:** 100% negative crypto test suite; containerized real-Hermes binary E2E integration test job; mandatory blocking step `digitalstate audit-evidence --check --all --federated` in GitHub Actions CI.

---

## 5. Scope Boundaries

### In Scope
- Full specification of remediation architecture for all identified PREMORTEM risks across Areas A-F.
- Encoding resolved architectural decisions (Key Management, CA Ownership, Hermes Trust Root, Offline Enrollment, Federation Attestation Policy).
- Construction of `SPEC.md`, `PLAN.md`, `TASKS.md`, and `RISK_REGISTER.md`.
- Definition of file-level engineering task breakdown, validation commands, and acceptance criteria.

### Out of Scope / Non-Goals
- Modifying repository code files during the current PLANNING & CLARIFICATION phase.
- Executing git commits, git tagging, or publishing release packages.
- Redesigning the underlying core `GovernanceKernel` state machine transitions.

---

## 6. Acceptance Criteria
1. **Bootstrap Atomicity:** `installer.py` dynamically computes ISO-8601 timestamps and guarantees complete directory cleanup on any bootstrap failure step.
2. **Keystore Security:** `keystore.py` replaces XOR cipher with AES-256-GCM / OS Keyring API, verified by key extraction test failure.
3. **Certificate Authenticity:** `enrollment.py` signs certificates with an ECDSA P-256 CA key; unsigned or pseudo-signed certificates fail validation.
4. **Federation Enforcement:** `manager.py` marks missing signature bundles as `is_valid = False` and returns non-zero exit status on audit.
5. **Ledger Integrity:** Concurrency stress test appending 100 concurrent entries to `audit_log.jsonl` yields `chain_intact: true` and `status: VALID`.
6. **CLI Exit Code Standard:** `digitalstate audit-evidence --check` returns exit code `1` on unverified records.
7. **CI Release Gate:** `.github/workflows/evidence-audit.yml` blocks PR merge if evidence audit fails.
