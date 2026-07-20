# Official Release Notes: Digital State v1.13.0-platform

We are pleased to announce the official release of **Digital State v1.13.0-platform** (Platform Evidence Integration & Governance Expansion). This release integrates the Evidence Governance Subsystem across all platform domains, introducing the `KernelEvidenceBridge`, `DeviceEvidenceValidator`, enhanced `digitalstate audit-evidence` CLI options (`--check`, `--all`), and automated CI/CD evidence verification workflows while preserving 100% frozen baseline compatibility with `v1.12.0-evidence` (`10635c6`).

---

## Key Capabilities Introduced in v1.13.0-platform

1. **Kernel Evidence Binding Bridge**:
   - `KernelEvidenceBridge` connects `EvidenceValidationEngine` to `WorkflowKernel` gate decisions and runtime provisioning.
2. **Device Runtime Evidence Validation**:
   - `DeviceEvidenceValidator` programmatically evaluates `.specify/device/` 4-file evidence bundles and outputs JSON manifests.
3. **Enhanced CLI Verification Subcommand**:
   - `digitalstate audit-evidence` supports `--check` (strict exit-code enforcement) and `--all` (platform-wide audit).
4. **Automated CI/CD Workflow Pipeline**:
   - GitHub Actions workflow `.github/workflows/evidence-audit.yml` automates evidence verification across Python 3.10-3.12 matrix on Ubuntu and Windows.

---

# Official Release Notes: Digital State v1.12.0-evidence


We are pleased to announce the official release of **Digital State v1.12.0-evidence** (Evidence Governance Framework Integration). This additive release introduces reusable evidence governance infrastructure to enforce evidence classification, boundary isolation, and negative-evidence rules across all future architectural reviews and audits while preserving 100% frozen baseline compatibility with `v1.11.0-device-verified` (`0abc5a8`).

---

## Key Capabilities Introduced in v1.12.0-evidence

1. **Canonical Evidence Classification Model**:
   - Enforces strict typed classifications: `VERIFIED`, `VERIFIED ABSENCE`, `NOT FOUND IN CURRENT OFFICIAL DOCUMENTATION`, and `UNVERIFIED`.
2. **Boundary Taxonomy & Isolation**:
   - Enforces explicit separation between Digital State Repository, Hermes Agent Framework, Python Packaging Specifications (PEP 427), and External Platform Behaviors.
3. **Negative-Evidence Governance Rules**:
   - Rules Engine (`EvidenceValidationEngine`) programmatically prevents documentation silence from being misclassified as proof of impossibility (`VERIFIED_ABSENCE`).
4. **Machine-Readable Governance Artifacts**:
   - Supports dual export format (Markdown Audit Tables and JSON Evidence Manifests) for automated CI/CD validation pipelines.
5. **Dynamic Repository Independence**:
   - Resolves workspace root dynamically without hardcoded filesystem paths.
6. **Additive Console Command**:
   - Added `digitalstate audit-evidence` CLI subcommand.

---

# Official Release Notes: Digital State v1.11.0-device


We are pleased to announce the official release of **Digital State v1.11.0-device** (Distributed Device Runtime Governance). This additive major feature release extends Digital State from single-repository governance to distributed host user devices while preserving 100% frozen baseline compatibility with `v1.10.0-production-verified` (`b4fd79687cac128bde2b237363382bc221d84c6a`).

---

## Key Capabilities Introduced in v1.11.0-device

1. **Phase 1 — Device Identity & Keystore Foundation (`digitalstate-device`)**:
   - ECDSA P-256 device keypair generation and cryptographic derivation (`device_id = SHA256(pubkey)`).
   - OS-level secure storage abstraction (`DeviceKeystore`) utilizing Windows DPAPI with machine-bound encrypted fallback. Zero plain-text private key disk persistence.
   - Standardized 4-file evidence bundle generation under `.specify/device/` (`device-status.json`, `identity-proof.json`, `runtime-attestation.json`, `policy-state.json`).
   - Additive console entrypoints: `digitalstate-device init`, `verify`, `doctor`, `verify-ledger`.
2. **Phase 2 — Local Device Runtime (`DeviceDaemon` & Policy Engine)**:
   - Sub-millisecond tool interception daemon (`DeviceDaemon`) listening strictly on local loopback socket (`127.0.0.1`).
   - Local Policy Engine (`LocalPolicyEngine`) enforcing Fail-Safe Default-Deny on missing context, malformed policies, or expired offline state.
   - Tamper-evident local audit log (`device_ledger.jsonl`) with line-by-line SHA-256 inter-line hash chaining.
3. **Phase 3 — Device Enrollment Protocol (`EnrollmentProtocol`)**:
   - 5-step cryptographic challenge-response enrollment handshake (`create_enrollment_request` $\rightarrow$ `generate_challenge_nonce` $\rightarrow$ `sign_challenge` $\rightarrow$ `verify_and_enroll`).
   - Strict rejection on invalid signatures, expired nonces, or missing keys.
   - `DeviceCertificate` metadata issuance (`.specify/device/device-certificate.json`).
4. **Phase 4 — SyncClient & Offline Enforcement (`SyncClient`)**:
   - Outbound TLS 1.3 secure communication client for downloading signed policies, checking CRL revocation lists, and uploading evidence bundles.
   - 3-State Offline Grace Period Enforcement (`ACTIVE` <12h, `WARNING` 12h–24h, `DEFAULT_DENY` >=24h). Expired offline state enforces Fail-Closed Default-Deny (`action: block`).

---

# Official Release Notes: Digital State v1.10.0


We are pleased to announce the official release of **Digital State v1.10.0**. This release establishes Cryptographic Audit Log Signature Chaining (012-audit-log-signature-chaining), Multi-Tenant Key Server Authentication (011-multi-tenant-key-server), and full Production Runtime Verification.

---

## Production Runtime Verification Completed

- **Hermes Runtime Provenance Verified**: End-to-end trace ID propagation (`HERMES_KANBAN_RUN_ID`) from Hermes Runtime origin (`hermes_agent.kanban.runner`) to plugin interception, governance decision, and ledger persistence fully verified.
- **Digital State Enforcement Path Verified**: Fail-Safe Default-Deny pre-tool-call interception verified (`HOOK_ENFORCEMENT_VERIFIED`) with 100% test suite pass rate (`67/67 passed`).
- **Ledger Integrity Verified**: SHA-256 inter-line signature hash chaining verified intact via `digitalstate verify-ledger` (`status: VALID`, `chain_intact: true`).

---

# Official Release Notes: Digital State v1.3


We are pleased to announce the official release of **Digital State v1.3**. This version establishes a unified user installation journey and resolves security boundaries to deliver a stable, evidence-gated governance framework for the Hermes Agent ecosystem.

---

## 1. Unified User Installation Journey

We have transformed the repository from a developer-only codebase into a package installer.

### Path A: Primary User Installation (GitHub Remote Package)
Installs the dependency directly into any Python project:
```bash
pip install git+https://github.com/samirhosninet/Digital-State.git
```
Users initialize and verify workspaces using:
```bash
digitalstate init
digitalstate doctor
```

### Path B: Developer Repository Installation (Local Clone Helpers)
For developers modifying the codebase or self-hosted environments, we maintain:
- **`install.ps1`** (Windows PowerShell helper)
- **`install.sh`** (Unix shell helper)

---

## 2. Refined Security Claims & Boundaries

Following deep architectural audits, we have refined the core security claim of Digital State:

* **Evidence-Gated Governance:** All feature state transitions, tool outcomes, and cryptographic signatures are verified and appended to the immutable local audit trail.
* **Hermes Hook Enforcement Boundary:** The Hermes client adapter is currently a **mock/simulation compatibility layer**. This version does not claim remote runtime enforcement or synchronous execution blocking.

---

## 3. Scope of Changes

- **Console Script Registry:** Added `digitalstate` entrypoint in `pyproject.toml`.
- **Diagnostics Utility (`digitalstate doctor`):** Added a structured JSON diagnostic checking Python runtimes, workspace configurations, state databases, and mock Hermes status.
- **Idempotent Initialization (`digitalstate init`):** Ensures reinstallation does not modify existing configurations.
- **Dynamic Path Cleaning:** Removed hardcoded drive letters in test suites to support clean system-independent CI validation.

---

## 4. Release Registry Detail
* **Release Tag:** `v1.3-release`
* **Release Commit:** `6c9ecea`
* **Documentation Validation Reference:** `c81d1d1`
* **Test Success Rate:** 100% (47/47 test cases passing)

---

# Official Release Notes: Digital State v1.9.0

We are pleased to announce the release of **Digital State v1.9.0**. This version delivers native Hermes runtime workflow integration and end-to-end reproducible self-governance lifecycle execution.

## 1. Native Hermes Runtime Integration
- **Local Self-Governance Runtime**: Added `governance/self-governance/runtime.py` as a single entrypoint coordinating Prime -> Builder -> Auditor -> Prime -> Human -> Release workflow sequence without external binary dependencies.
- **Spec Kit Artifact Generation**: Automatically generates spec, plan, and tasks artifacts directly from repo `.specify/templates/`.
- **Hermes Kanban Orchestration**: Drives lifecycle transitions through `KanbanOrchestrator` backed by `WorkflowKernel` transition rules.

## 2. Release Detail
- **Release Tag**: `v1.9-runtime-integration`
- **Release Commit**: `b3fbe47aed8bf41073b94a1e6b39d935aee8436e`
- **Test Success Rate**: 100% (58/58 test cases passing)

---

# Official Release Notes: Digital State v1.9.1

We are pleased to announce the release of **Digital State v1.9.1**. This release establishes production-trust runtime authentication and end-to-end governance validation.

## 1. Runtime Authentication (DS-RUNTIME-AUTH-004 / ADR-013 Option E)
- **3-Tier Context Adapter**: Resolves `feature_id` and `agent_key` across explicit context dictionary (Tier 1), process environment variables (Tier 2), and `RuntimeStore` identity records with workspace state fallback (Tier 3).
- **Fail-Safe Default-Deny**: Preserves strict default-deny enforcement across all 6 Hermes lifecycle hooks.

## 2. Governance Context Loader & Event Parametrization (DS-END-TO-END-INSTALL-VALIDATION-001)
- **Governance Context Loading**: Added `load_governance_context()` in `runtime.py` to parse, validate, and record `governance/CONSTITUTION_v1.md`, `specs/ARCHITECTURE.md`, and profile templates as `GOVERNANCE_LOAD` into the ledger.
- **CLI Parametrization**: Supports `--new <feature>` and `--event <event>` to execute governance workflow sequences for arbitrary features from a clean install.

## 3. Release Detail
- **Release Tag**: `v1.9.1`
- **Release Commit**: `7011ece324c0d0c3eb1496a71e217036a9ea100e`
- **GitHub Release URL**: `https://github.com/samirhosninet/Digital-State/releases/tag/v1.9.1`
- **Test Success Rate**: 100% (64/64 test cases passing)

