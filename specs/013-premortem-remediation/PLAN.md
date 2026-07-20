# Implementation Plan: PREMORTEM Engineering Remediation (v1.16.0-remediation)

## Implementation Overview
This plan establishes a phased, non-breaking remediation path to address all 18 PREMORTEM risks identified across 6 core technical domains in the Digital State repository baseline `v1.15.0`, incorporating the 5 clarified architectural decisions.

---

## 1. Ordered Implementation Phases

### Phase 1: Cryptographic Foundation & Keystore Hardening (Area B)
- **Goal:** Eliminate insecure fallback ciphers, implement true CA signing, and add certificate auto-renewal.
- **Architectural Clarifications Applied:**
  - *Key Management:* Implement 2-Tier OS Keyring (`win32crypt`/`Keychain`/`SecretService`) with AES-256-GCM / PBKDF2 fallback for headless environments.
  - *CA Ownership:* Provision ECDSA P-256 Local CA during `init` and integrate with `ADR-011` Key Server.
- **Tasks:**
  1. Replace XOR fallback in `src/digital_state/device/keystore.py` with FIPS-compliant AES-256-GCM / OS Keyring abstraction (`keyring` / PBKDF2).
  2. Implement ECDSA P-256 Authority signature generation for `device-certificate.json` in `src/digital_state/device/enrollment.py`.
  3. Implement certificate renewal command (`digitalstate-device renew-cert`) and daemon auto-renewal logic when certificate expiration is `< 14 days`.

### Phase 2: Bootstrap & Installation Atomicity (Area A)
- **Goal:** Fix non-atomic operations, static timestamps, and environment dependencies in installers.
- **Tasks:**
  1. Update `src/digital_state/bootstrap/installer.py` to use dynamic UTC ISO-8601 timestamps.
  2. Implement transactional rollback wrapper in `BootstrapInstaller` to erase partially created `.specify/` state on error.
  3. Refactor `auto_configure_hermes()` to write `config.yaml.tmp` and perform atomic file replacement via `os.replace()`.
  4. Fix absolute script directory resolution in `install.ps1` and `install.sh` for non-root execution.

### Phase 3: Evidence Governance & Multi-Tenant Federation Hardening (Area C)
- **Goal:** Close federation attestation bypasses and prevent concurrency ledger corruption.
- **Architectural Clarification Applied:**
  - *Attestation Policy:* Strict Fail-Closed Default-Deny (`is_valid = False`, `failed_devices += 1`) on missing signature fields.
- **Tasks:**
  1. Refactor `FederatedEvidenceManager` in `src/digital_state/governance/federation/manager.py` to enforce strict Default-Deny (`is_valid = False`, `failed_devices += 1`) when attestation signatures are missing.
  2. Add OS cross-process `FileLock` wrapper around `audit_log.jsonl` and `device_ledger.jsonl` appends in `src/digital_state/device/device_ledger.py` and `src/digital_state/core/engine.py`.
  3. Extend `DeviceEvidenceValidator` to perform deep JSON schema and cryptographic signature verification on 4-file evidence bundles.

### Phase 4: Hermes Integration & Profile Verification (Area D)
- **Goal:** Secure runtime context resolution and prevent profile spoofing.
- **Architectural Clarifications Applied:**
  - *Trust Root:* Cryptographically signed session token verification instead of trusting process environment variables.
  - *Offline Policy:* Enforce 3-State Grace Period Policy (`ACTIVE` <12h, `WARNING` 12-24h, `DEFAULT_DENY` >=24h).
- **Tasks:**
  1. Implement fail-closed session abort in `DigitalStatePlugin` (`src/digital_state/hermes/plugin.py`) when context resolution returns invalid metadata.
  2. Replace process environment variable trusting (`HERMES_PROFILE`) with cryptographically signed session tokens.
  3. Add structured exception handling and audit ledger reporting for uncaught lifecycle hook errors.

### Phase 5: CLI Standardization & Admin Workflows (Area E)
- **Goal:** Standardize CLI exit codes and complete administrative subcommands.
- **Tasks:**
  1. Standardize CLI return codes in `src/digital_state/cli/cli.py` and `src/digital_state/device/cli.py` (`0`: Success, `1`: Governance Rejection, `2`: Parameter Error, `3`: I/O Error).
  2. Remove deprecated `--key` parameter and implement strict schema parsing in `create_parser()`.
  3. Fully implement `upgrade`, `uninstall`, and `repair` CLI command handlers and align documentation in `docs/USER_INSTALLATION_GUIDE.md`.

### Phase 6: Testing & CI/CD Release Engineering (Area F)
- **Goal:** Ensure complete negative test coverage and hard CI blocking gates.
- **Tasks:**
  1. Add negative cryptographic test suite in `tests/unit/test_negative_crypto.py`.
  2. Create containerized real-Hermes binary E2E integration test workflow `.github/workflows/e2e-hermes.yml`.
  3. Add mandatory blocking step `digitalstate audit-evidence --check --all --federated` in `.github/workflows/evidence-audit.yml`.

---

## 2. Dependencies
- `Phase 2` (Bootstrap) depends on `Phase 1` (Keystore) for proper device key provisioning during zero-touch setup.
- `Phase 3` (Federation) depends on `Phase 1` (Crypto) for authentic certificate verification.
- `Phase 5` (CLI) depends on `Phase 3` (Evidence) for correct exit code propagation on audit checks.
- `Phase 6` (Testing) depends on all previous phases (1-5) to validate complete remediation.

---

## 3. Migration Strategy
1. **Keystore Format Upgrade:** Existing `keystore.enc` files utilizing legacy `ENC:` prefix will be transparently migrated to AES-256-GCM / OS Keyring format upon first execution of `digitalstate-device verify` or `digitalstate doctor`.
2. **Federation Manifest Version bump:** Upgrades federated evidence manifest schema version from `v2.0` to `v2.1-authenticated` with explicit backward compatibility reader.
3. **Zero Downtime:** Daemon and plugin changes preserve state file backwards compatibility with `.specify/state.json`.

---

## 4. Rollback Strategy
1. If Phase 1 (Keystore) encounters OS keyring access issues on legacy OS platforms, the system falls back to PBKDF2 AES-256-GCM machine-encrypted storage (never plain text or XOR).
2. If Phase 3 (FileLock) hits NFS/network mount file lock limitations, a fallback file lock timeout with diagnostic warning is logged.
3. Rollback of codebase to certified baseline `v1.15.0` (`5950f9d`) is preserved via git branch isolation (`feature/013-premortem-remediation`).

---

## 5. Testing Strategy
- **Unit Tests:** `pytest tests/unit/` (target 100% pass rate across 35 test files).
- **Negative Tests:** `pytest tests/unit/test_negative_crypto.py`.
- **Concurrency Tests:** `pytest tests/integration/test_concurrency.py` with 100 parallel worker threads appending ledger entries.
- **CI Blocking Gate:** `digitalstate audit-evidence --check --all --federated` returning exit code `0`.
