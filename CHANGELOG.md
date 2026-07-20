# Changelog

All notable changes to the Digital State project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.16.0] - 2026-07-20

### Added
- Complete PREMORTEM engineering remediation release (`v1.16.0`).
- FIPS-compliant AES-256-GCM authenticated key encryption with PBKDF2 (100,000 iterations) key derivation in `DeviceKeystore`.
- Authentic ECDSA P-256 Certificate Authority (CA) signature generation & verification (`verify_certificate()`, `renew_certificate()`).
- Added `digitalstate-device renew-cert` CLI command and background daemon auto-renewal when certificate expiration is `< 14 days`.
- Cross-process `FileLock` (`msvcrt` / `fcntl`) protection for `device_ledger.jsonl` appends.
- Fail-Closed Default-Deny attestation policy in `FederatedEvidenceManager` and deep JSON schema/signature validation in `DeviceEvidenceValidator`.
- Cryptographically signed session token verification in `adapter.py` and fail-closed session abort in `DigitalStatePlugin`.
- Standardized CLI return codes (`0`: success, `1`: rejection, `2`: args, `3`: I/O) and implemented `repair`, `upgrade`, and `uninstall` command handlers.
- Negative cryptographic test suite `tests/unit/test_negative_crypto.py` and containerized live-Hermes workflow `.github/workflows/e2e-hermes.yml`.

## [1.15.0] - 2026-07-20


### Added
- Multi-Tenant Evidence Federation & Remote Attestation Protocol (`v1.15.0`).
- Additive module `digital_state.governance.federation` providing `FederatedEvidenceManager` and `RemoteAttestationVerifier`.
- Cryptographic remote attestation verification using device ECDSA P-256 identity keypair challenge-response nonces.
- CLI subcommand `digitalstate audit-evidence` enhancement adding `--federated` option for rendering multi-tenant JSON manifests.

### Changed
- Incremented package version in `pyproject.toml` to `1.15.0`.

## [1.14.0-bootstrap] - 2026-07-20


### Added
- Zero-touch installation & first-run bootstrap protocol (`v1.14.0-bootstrap`).
- Official cross-platform installers `install.ps1` (Windows PowerShell) and `install.sh` (POSIX Shell) with `--dry-run` pre-flight support.
- `BootstrapSubsystem` (`digital_state.bootstrap`) containing `PrerequisiteChecker` and `BootstrapInstaller`.
- Hermes Desktop integration auto-detection, `config.yaml` plugin registration, and profile seeding (`prime`, `builder`, `auditor`).
- Cryptographic `EnrollmentProtocol` challenge-response handshake execution during bootstrap.
- Automated `verify_installation_health` hook logging doctor and evidence verification status in `.specify/integration.json`.
- End-user onboarding documentation `docs/USER_INSTALLATION_GUIDE.md`.

### Changed
- Incremented package version in `pyproject.toml` to `1.14.0`.

## [1.13.0-platform] - 2026-07-20


### Added
- Integrated Evidence Governance Subsystem across all platform subsystems (`v1.13.0-platform`).
- `KernelEvidenceBridge` (`digital_state.governance.evidence.kernel_bridge`) for binding evidence engine with WorkflowKernel gate decisions and runtime provisioning.
- `DeviceEvidenceValidator` (`digital_state.governance.evidence.device_validator`) for validating 4-file device evidence bundles and generating manifests.
- CLI subcommand `digitalstate audit-evidence` enhancements adding `--check` (strict exit code enforcement) and `--all` (platform-wide audit).
- GitHub Actions automated evidence verification workflow `.github/workflows/evidence-audit.yml`.

### Changed
- Incremented package version in `pyproject.toml` to `1.13.0`.

## [1.12.0-evidence] - 2026-07-20


### Added
- Additive module `digital_state.governance.evidence` providing reusable Evidence Governance infrastructure.
- `EvidenceRecord` dataclass supporting stable UUIDs, schema versioning (`v1.0`), commit references, and provenance timestamps.
- `EvidenceValidationEngine` enforcing positive evidence checks, PEP 427 wheel spec rules, and boundary isolation.
- `EvidenceReportGenerator` supporting dual Markdown and JSON output formats.
- Additive console subcommand `digitalstate audit-evidence`.
- Specification documentation `docs/EVIDENCE_GOVERNANCE_SPEC.md`.

### Changed
- Incremented package version in `pyproject.toml` to `1.12.0`.

## [1.11.0-device] - 2026-07-19

### Added
- Additive module `digital_state.device` providing Distributed Device Runtime Governance.
- ECDSA P-256 device keypair generation and OS keystore DPAPI abstraction.
- 4-file local evidence bundle manager under `.specify/device/`.
- Local IPC interception daemon (`DeviceDaemon`) bound strictly to loopback (`127.0.0.1`).
- Sub-millisecond policy engine (`LocalPolicyEngine`) enforcing Fail-Safe Default-Deny.
- Cryptographic local audit log (`device_ledger.jsonl`) with line-by-line SHA-256 hash chaining.
- Cryptographic challenge-response enrollment protocol (`EnrollmentProtocol`).
- Secure outbound TLS 1.3 sync client (`SyncClient`) with offline grace period enforcement.
