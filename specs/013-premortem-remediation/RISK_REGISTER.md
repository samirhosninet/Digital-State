# Risk Register: PREMORTEM Vulnerability Matrix (v1.16.0-remediation)

## Risk Classification Scale
- **Probability:** High (H), Medium (M), Low (L)
- **Severity:** Critical (C), High (H), Medium (M), Low (L)

---

## Identified Risks & Remediation Controls (Updated with Clarified Architecture)

| Risk ID | Category | Risk Description | Prob | Sev | Detection Method | Prevention Mechanism | Owner Responsibility |
|---|---|---|---|---|---|---|---|
| **RISK-01** | Installation & Bootstrap | **Static Hardcoded Timestamp**: `installer.py:81` hardcodes `"2026-07-20T04:35:00Z"`. | **H** | **M** | Static analysis / `test_bootstrap.py` timestamp comparison. | Use `datetime.now(timezone.utc).isoformat()` dynamically. | Release Engineer / Bootstrap Lead |
| **RISK-02** | Installation & Bootstrap | **Non-Atomic Bootstrap Setup**: Partial setup failure leaves corrupt `.specify/` without cleanup. | **M** | **H** | Run installer with invalid permissions or mocked exception. | Transactional try/except rollback handler deleting created paths. | Core Infrastructure Lead |
| **RISK-03** | Installation & Bootstrap | **In-Place Config Truncation**: Mutating Hermes `config.yaml` directly without `.tmp` file swap. | **M** | **H** | Process interruption test during `yaml.safe_dump`. | Write to `config.yaml.tmp` then `os.replace()`. | Hermes Integration Lead |
| **RISK-04** | Installation & Bootstrap | **Environment Path Failure**: `install.ps1`/`install.sh` fail if run outside repo root. | **H** | **M** | Execute installer from external working directory. | Resolve script absolute path dynamically (`PSScriptRoot` / `BASH_SOURCE`). | DevOps / Tooling Lead |
| **RISK-05** | Identity & Cryptography | **Trivial XOR Cipher Key Exposure**: Non-Windows keystore uses XOR with hostname string. | **H** | **C** | Known-plaintext XOR key derivation script. | **2-Tier Model:** FIPS AES-256-GCM + PBKDF2 (100k iter) / OS Keyring. | Security / Crypto Lead |
| **RISK-06** | Identity & Cryptography | **Fake Certificate Signatures**: `enrollment.py:121` uses `secrets.token_hex(64)` as cert signature. | **H** | **C** | Signature verification with public key yields parser error. | **CA Ownership Model:** Issue certs signed by ECDSA P-256 Authority keypair. | Security / Crypto Lead |
| **RISK-07** | Identity & Cryptography | **Missing Certificate Renewal**: 90-day expiry without renewal protocol causes permanent failure. | **H** | **H** | System clock forward simulation (+91 days). | Add `digitalstate-device renew-cert` CLI & background daemon auto-renewal. | Device Daemon Lead |
| **RISK-08** | Evidence Governance | **Attestation Bypass in Federation**: Missing signature sets `is_valid = True` ("Attestation omitted."). | **H** | **C** | Aggregate bundle with empty signature; verify `verified_devices`. | **Attestation Policy:** Strict Default-Deny (`is_valid = False`, `UNVERIFIED`). | Governance Engine Lead |
| **RISK-09** | Evidence Governance | **Ledger Hash-Chain Corruption**: Concurrent appends to `.jsonl` corrupt inter-line hash chain. | **M** | **H** | Multithreaded stress test appending 100 concurrent logs. | Cross-process file locking wrapper (`FileLock`) around appends. | Storage / Ledger Lead |
| **RISK-10** | Evidence Governance | **Superficial Evidence Bundle Audit**: `DeviceEvidenceValidator` checks file existence only, not content/schema. | **H** | **H** | Pass empty 0-byte JSON files to validator. | Perform deep JSON schema and cryptographic signature verification. | Auditor Lead |
| **RISK-11** | Hermes Integration | **Silent Context Resolution Fallback**: Unhandled context resolution allows unmonitored tool execution. | **M** | **H** | Invoke plugin with empty/malformed `ctx`. | Mandatory Fail-Closed session block on context resolution failure. | Runtime Integration Lead |
| **RISK-12** | Hermes Integration | **Agent Profile Spoofing**: Trusting process environment variables (`HERMES_PROFILE`) for identity. | **H** | **H** | Execute session with spoofed `HERMES_PROFILE` env var. | **Trust Root Model:** Signed session token payload verification. | Security Lead |
| **RISK-13** | Hermes Integration | **Unhandled Hook Exception Masking**: Hook errors caught silently without diagnostic logging. | **M** | **M** | Inject synthetic exception in `pre_tool_call_handler`. | Log structured error event and append to audit ledger. | Runtime Integration Lead |
| **RISK-14** | CLI / UX | **Silent Failure Exit Code 0**: CLI failures print error text but return exit code `0`. | **H** | **H** | Execute `digitalstate audit-evidence --check` on bad data; inspect exit code. | Standardize return codes (`0`: success, `1`: failure, `2`: args, `3`: I/O). | CLI Lead |
| **RISK-15** | CLI / UX | **Deprecated Parameter Confusion**: CLI accepts deprecated `--key` flag without rejection. | **L** | **L** | Run `digitalstate register --key "foo"`. | Remove deprecated flags and enforce strict `argparse` validation. | UX Lead |
| **RISK-16** | CLI / UX | **Stubbed Admin Commands**: `upgrade`, `uninstall`, `repair` are stubbed or incomplete in `cli.py`. | **M** | **M** | Execute `digitalstate repair` on damaged workspace. | Implement full command handlers with rollback protection. | Maintenance Lead |
| **RISK-17** | Testing & Release | **Missing Negative Crypto Tests**: Happy-path tests obscure invalid curve or tampered payload bugs. | **H** | **H** | Code coverage inspection of cryptographic error paths. | Construct 100% negative crypto test suite in `test_negative_crypto.py`. | QA / Testing Lead |
| **RISK-18** | Testing & Release | **CI Evidence Enforcement Gap**: CI runs unit tests but does not block releases on evidence audit failure. | **H** | **H** | Submit PR with unverified evidence records; inspect CI status. | Enforce `digitalstate audit-evidence --check --all --federated` as blocking step. | CI/CD Release Lead |
