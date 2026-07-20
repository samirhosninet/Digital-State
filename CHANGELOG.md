# Changelog

All notable changes to the Digital State project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
