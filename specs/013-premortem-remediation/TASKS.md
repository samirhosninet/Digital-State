# Engineering Tasks: PREMORTEM Remediation (v1.16.0-remediation)

## Task Breakdown Matrix

### Phase 1: Cryptographic Foundation & Keystore Hardening
- [ ] `TASK-013-B1`: Replace XOR cipher in keystore fallback with FIPS-compliant AES-256-GCM / OS Keyring (`keyring` / PBKDF2).
  - **Module Impact:** `src/digital_state/device/keystore.py`
  - **Required Tests:** `tests/unit/test_cryptography.py::test_keystore_aes_gcm_security`
  - **Validation Command:** `pytest tests/unit/test_cryptography.py`
- [ ] `TASK-013-B2`: Implement true ECDSA P-256 Authority signature generation for `device-certificate.json`.
  - **Module Impact:** `src/digital_state/device/enrollment.py`
  - **Required Tests:** `tests/unit/test_device_enrollment.py::test_authority_certificate_signature_verification`
  - **Validation Command:** `pytest tests/unit/test_device_enrollment.py`
- [ ] `TASK-013-B3`: Implement certificate renewal protocol (`digitalstate-device renew-cert`) and daemon auto-renewal.
  - **Module Impact:** `src/digital_state/device/cli.py`, `src/digital_state/device/device_daemon.py`
  - **Required Tests:** `tests/unit/test_device_cli.py::test_cert_renewal_flow`
  - **Validation Command:** `python -m digital_state.device.cli renew-cert --help`

---

### Phase 2: Bootstrap & Installation Atomicity
- [ ] `TASK-013-A1`: Dynamically compute UTC ISO-8601 timestamps in `installer.py` (`installed_at`).
  - **Module Impact:** `src/digital_state/bootstrap/installer.py`
  - **Required Tests:** `tests/unit/test_bootstrap.py::test_dynamic_timestamp_generation`
  - **Validation Command:** `pytest tests/unit/test_bootstrap.py`
- [ ] `TASK-013-A2`: Add transactional rollback cleanup handler to `BootstrapInstaller` for partial setup failures.
  - **Module Impact:** `src/digital_state/bootstrap/installer.py`
  - **Required Tests:** `tests/unit/test_bootstrap.py::test_installer_rollback_on_failure`
  - **Validation Command:** `pytest tests/unit/test_bootstrap.py`
- [ ] `TASK-013-A3`: Refactor `auto_configure_hermes()` to perform atomic file writing (`config.yaml.tmp` $\rightarrow$ `config.yaml`).
  - **Module Impact:** `src/digital_state/bootstrap/installer.py`
  - **Required Tests:** `tests/unit/test_bootstrap.py::test_hermes_config_atomic_mutation`
  - **Validation Command:** `pytest tests/unit/test_bootstrap.py`
- [ ] `TASK-013-A4`: Fix script directory resolution in `install.ps1` and `install.sh` for external execution paths.
  - **Module Impact:** `install.ps1`, `install.sh`
  - **Required Tests:** `tests/integration/test_installation.py::test_external_directory_installation`
  - **Validation Command:** `powershell -ExecutionPolicy Bypass -File install.ps1 -DryRun`

---

### Phase 3: Evidence Governance & Multi-Tenant Federation
- [ ] `TASK-013-C1`: Refactor `FederatedEvidenceManager` to enforce Default-Deny (`is_valid = False`, `failed_devices += 1`) on omitted attestation fields.
  - **Module Impact:** `src/digital_state/governance/federation/manager.py`
  - **Required Tests:** `tests/unit/test_evidence_federation.py::test_omitted_attestation_rejection`
  - **Validation Command:** `pytest tests/unit/test_evidence_federation.py`
- [ ] `TASK-013-C2`: Implement cross-process `FileLock` protection for `audit_log.jsonl` and `device_ledger.jsonl` appends.
  - **Module Impact:** `src/digital_state/device/device_ledger.py`, `src/digital_state/core/engine.py`
  - **Required Tests:** `tests/integration/test_concurrency.py::test_concurrent_ledger_append_locking`
  - **Validation Command:** `pytest tests/integration/test_concurrency.py`
- [ ] `TASK-013-C3`: Extend `DeviceEvidenceValidator` to validate deep JSON schemas and signature integrity of 4-file evidence bundles.
  - **Module Impact:** `src/digital_state/governance/evidence/device_validator.py`
  - **Required Tests:** `tests/unit/test_evidence_device_validator.py::test_bundle_schema_and_signature_validation`
  - **Validation Command:** `pytest tests/unit/test_evidence_device_validator.py`

---

### Phase 4: Hermes Integration & Profile Verification
- [ ] `TASK-013-D1`: Add fail-closed session abort in `DigitalStatePlugin` on governance context resolution failure.
  - **Module Impact:** `src/digital_state/hermes/plugin.py`
  - **Required Tests:** `tests/unit/test_plugin.py::test_fail_closed_context_resolution_failure`
  - **Validation Command:** `pytest tests/unit/test_plugin.py`
- [ ] `TASK-013-D2`: Replace `HERMES_PROFILE` environment variable reliance with signed session tokens.
  - **Module Impact:** `src/digital_state/hermes/plugin.py`, `src/digital_state/runtime/adapter.py`
  - **Required Tests:** `tests/unit/test_runtime_identity_resolution.py::test_signed_session_token_verification`
  - **Validation Command:** `pytest tests/unit/test_runtime_identity_resolution.py`
- [ ] `TASK-013-D3`: Implement structured exception reporting and audit logging for lifecycle hook errors.
  - **Module Impact:** `src/digital_state/hermes/plugin.py`
  - **Required Tests:** `tests/unit/test_plugin.py::test_hook_exception_audit_logging`
  - **Validation Command:** `pytest tests/unit/test_plugin.py`

---

### Phase 5: CLI Standardization & Admin Workflows
- [ ] `TASK-013-E1`: Standardize CLI exit codes across `cli.py` and `device/cli.py` (`0` success, `1` rejection, `2` args, `3` I/O).
  - **Module Impact:** `src/digital_state/cli/cli.py`, `src/digital_state/device/cli.py`
  - **Required Tests:** `tests/unit/test_cli_commands.py::test_exit_code_standardization`
  - **Validation Command:** `python -m digital_state.cli.cli audit-evidence --check`
- [ ] `TASK-013-E2`: Remove deprecated `--key` parameter and enforce strict `argparse` validation.
  - **Module Impact:** `src/digital_state/cli/cli.py`
  - **Required Tests:** `tests/unit/test_cli_commands.py::test_deprecated_key_flag_rejection`
  - **Validation Command:** `pytest tests/unit/test_cli_commands.py`
- [ ] `TASK-013-E3`: Implement complete handlers for `upgrade`, `uninstall`, and `repair` CLI commands.
  - **Module Impact:** `src/digital_state/cli/cli.py`, `docs/USER_INSTALLATION_GUIDE.md`
  - **Required Tests:** `tests/unit/test_recovery.py::test_cli_repair_and_uninstall_handlers`
  - **Validation Command:** `pytest tests/unit/test_recovery.py`

---

### Phase 6: Testing & CI/CD Release Engineering
- [ ] `TASK-013-F1`: Construct negative cryptographic test suite `tests/unit/test_negative_crypto.py`.
  - **Module Impact:** `tests/unit/test_negative_crypto.py` [NEW]
  - **Required Tests:** `tests/unit/test_negative_crypto.py`
  - **Validation Command:** `pytest tests/unit/test_negative_crypto.py`
- [ ] `TASK-013-F2`: Add containerized real-Hermes binary E2E integration test workflow `.github/workflows/e2e-hermes.yml`.
  - **Module Impact:** `.github/workflows/e2e-hermes.yml` [NEW]
  - **Required Tests:** E2E container execution
  - **Validation Command:** `git check-ref-format`
- [ ] `TASK-013-F3`: Add mandatory blocking step `digitalstate audit-evidence --check --all --federated` in `evidence-audit.yml`.
  - **Module Impact:** `.github/workflows/evidence-audit.yml`
  - **Required Tests:** GitHub Actions validation
  - **Validation Command:** `pytest tests/unit/test_evidence_cli.py`
