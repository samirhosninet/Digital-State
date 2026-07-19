# Changelog

All notable changes to the Digital State project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
