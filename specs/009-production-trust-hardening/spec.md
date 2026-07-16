# Feature Specification: Production Trust Hardening

**Feature Branch**: `009-production-trust-hardening`  
**Created**: 2026-07-16  
**Status**: Draft  
**Input**: Remediate the end-to-end pre-mortem findings so Digital State provides verifiable cryptographic identity, truthful Hermes runtime status, tamper-evident audit accountability, safe recovery, and release gates backed by real clean-environment validation.

## User Scenarios & Testing

### User Story 1 - Trust a Production Governance Decision (Priority: P1)

As a governance operator, I can accept an evidence submission or transition only when it is tied to a valid cryptographic identity and the required independent role, so approvals cannot be forged using publicly known placeholder values.

**Why this priority**: A governance product cannot make trustworthy authorization claims while its default identity model is forgeable.

**Independent Test**: Register valid role identities, submit correctly signed evidence, and confirm that altered evidence, plaintext keys, self-approval, and cross-role approval attempts are rejected and auditable.

**Acceptance Scenarios**:

1. **Given** a registered active agent with a valid cryptographic public key, **When** it submits correctly signed evidence, **Then** the applicable gate can validate it and records the signer identity in the audit history.
2. **Given** an unknown, malformed, legacy plaintext, expired, or revoked identity, **When** it submits evidence or approves a gate, **Then** the action is rejected without changing lifecycle state.
3. **Given** an agent that authored work requiring independent approval, **When** that same agent attempts approval or verification, **Then** the system rejects the action and records the denial.

---

### User Story 2 - Know the Real Runtime Boundary (Priority: P1)

As an integrator, I can distinguish a live Hermes runtime from a simulated one before relying on enforcement, so a successful local simulation is never represented as live enforcement.

**Why this priority**: False runtime claims cause users to delegate real decisions to controls that may not be present.

**Independent Test**: Run diagnostics with no Hermes executable, with a known fake executable, and with a verified supported Hermes executable; confirm each reports an unambiguous state and that unsupported runtime invocation is denied.

**Acceptance Scenarios**:

1. **Given** Hermes is unavailable, **When** an operator runs diagnostics, **Then** the report is failing or explicitly unavailable and does not label the adapter live.
2. **Given** a simulation is run, **When** it succeeds, **Then** its result is labelled simulated and cannot satisfy the live-runtime release requirement.
3. **Given** a live runtime handshake has completed, **When** diagnostics run, **Then** the report includes the verified executable, version, handshake result, and timestamp.

---

### User Story 3 - Investigate Tampering and Recover Safely (Priority: P2)

As an auditor, I can detect a modified or inconsistent governance record and recover only through an explicit, traceable procedure, so recovery never silently destroys evidence or reconstructs untrusted state.

**Why this priority**: Audit data is the foundation of accountability; silent repair defeats that foundation.

**Independent Test**: Tamper with a persisted record, verify startup and audit checks fail closed, then execute a confirmed recovery using a validated backup and confirm both the incident and recovery are recorded.

**Acceptance Scenarios**:

1. **Given** a modified, truncated, or missing audit record, **When** the system starts or verifies integrity, **Then** it fails closed with a precise integrity finding.
2. **Given** an invalid state file, **When** an operator requests repair without an approved recovery source, **Then** no state is replaced and the command exits with an actionable error.
3. **Given** an approved valid recovery source, **When** recovery completes, **Then** the pre-recovery data is preserved, the restored state is validated, and the event is logged.

---

### User Story 4 - Release Only What Was Actually Validated (Priority: P2)

As a release owner, I can publish only an artifact that passed repeatable clean-environment installation, upgrade, removal, and security checks, so release reports are evidence rather than declarations.

**Why this priority**: Historical test reports and a dirty checkout cannot establish present release readiness.

**Independent Test**: Run the release gate in a clean temporary environment and verify it rejects dirty source trees, absent required tools, failing installation paths, failed test suites, and missing runtime evidence.

**Acceptance Scenarios**:

1. **Given** a dirty working tree or untracked sensitive material, **When** the release gate runs, **Then** it fails before packaging or publishing.
2. **Given** a fresh supported environment, **When** the release workflow runs, **Then** it builds an artifact, performs install, initialization, diagnostics, upgrade, removal, and post-removal checks using the public command paths.
3. **Given** any validation step fails or is skipped, **When** a release report is generated, **Then** it states not ready and contains the command outcome and immutable run metadata.

### Edge Cases

- A cryptographic key record is validly formatted but has an unsupported algorithm, key version, or revocation status.
- The audit log is internally valid but does not match persisted lifecycle state.
- A process dies while holding a governance lock or while an atomic state update is in progress.
- Hermes is installed but responds with an unsupported version or incomplete hook contract.
- A release environment lacks the project’s preferred runner or network access needed for dependency installation.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST reject legacy plaintext-key evidence verification and plaintext-key default agent registration in production operation.
- **FR-002**: The system MUST require a supported cryptographic public-key identity, active status, and authorized role for every evidence submission, approval, and execution authorization.
- **FR-003**: The system MUST prevent an agent from approving, verifying, or authorizing its own governed work where independent approval is required.
- **FR-004**: The system MUST record accepted and denied security-relevant actions with the responsible identity, outcome, timestamp, and reason.
- **FR-005**: The system MUST report Hermes availability, simulation status, runtime compatibility, and live handshake evidence as distinct, non-interchangeable states.
- **FR-006**: The system MUST fail closed when audit integrity or lifecycle-state consistency cannot be verified.
- **FR-007**: The system MUST require explicit recovery intent and a validated recovery source before replacing, rebuilding, or discarding governance state; it MUST preserve the pre-recovery material.
- **FR-008**: The release workflow MUST reject a dirty source tree, secret-like tracked or untracked material, failed validation, or a missing required evidence item.
- **FR-009**: The release workflow MUST validate the documented public installation, initialization, diagnosis, upgrade, removal, and recovery journeys in a newly created supported environment.
- **FR-010**: Release evidence MUST identify the artifact, source revision, environment, runtime mode, executed checks, and pass/fail outcome.

### Key Entities

- **Cryptographic Identity**: A versioned public-key identity with algorithm, status, authorized role, and lifecycle timestamps.
- **Authorization Decision**: An auditable accept/deny record relating an identity, action, feature, role rule, and reason.
- **Runtime Attestation**: A time-bound report of the Hermes mode, executable, version, compatibility, and handshake result.
- **Recovery Package**: A preserved pre-recovery snapshot, approved recovery input, validation result, and recovery audit event.
- **Release Evidence Bundle**: The traceable record of source revision, artifact, environment, commands, results, and release decision.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of attempts using plaintext, malformed, revoked, unsupported, or invalid identities are denied without changing governance state in automated security tests.
- **SC-002**: 100% of runtime diagnostic outputs classify the runtime as unavailable, simulated, incompatible, or live-verified; no simulated result is accepted as live verification.
- **SC-003**: 100% of deliberate audit or lifecycle-state tampering tests fail closed and leave the original evidence available for investigation.
- **SC-004**: A clean-environment release validation completes the documented installation and lifecycle journeys with no skipped mandatory check, and records a verifiable pass/fail bundle.
- **SC-005**: The release gate rejects 100% of intentionally dirty-tree, secret-scan, and failed-validation test cases.

## Assumptions

- The supported production deployment initially targets local workspaces with a clearly documented trust boundary; remote immutable storage may be introduced as a later capability.
- ECDSA P-256 public-key verification remains the supported signing standard for this release.
- A live Hermes claim is allowed only when a supported installed runtime completes the project's defined handshake; otherwise the product remains explicitly simulation-only.
- Existing data using plaintext keys must be migrated deliberately and must not silently retain production authorization capability.
- The existing user’s uncommitted changes and local keys are outside this feature’s ownership and will not be deleted or overwritten.
