# Feature Specification: Production Hardening

**Feature Branch**: `002-production-hardening`

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: "Advance the Governance Kernel from the approved baseline toward production readiness. Scope covers production cryptography, transactional persistence, concurrency models, recovery checks, operational hardening, and performance validation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Production Cryptographic Signatures (Priority: P1)

As an **Auditor** agent, I want every submitted checkpoint evidence payload to be verified using cryptographic keys, so that no actor can forge or tamper with submissions.

**Why this priority**: Crucial for security, preventing signature forgery which is the most critical remaining risk.

**Independent Test**: Can be validated by submitting evidence signed with an invalid/forged private key and verifying that the kernel rejects the signature with an `EvidenceError`.

**Acceptance Scenarios**:

1. **Given** a registered agent has ECDSA P-256 public key credentials in the registry, **When** they submit evidence signed with their valid private key, **Then** the signature is verified using ECDSA with SHA-256, and the evidence is accepted.
2. **Given** a registered agent, **When** they submit evidence signed with a forged or incorrect key, **Then** the validation fails, and the action is blocked.

---

### User Story 2 - Transactional Persistence & Concurrency Locking (Priority: P1)

As a **Builder** agent, I want to execute CLI commands concurrently without corrupting the state file or audit log, so that parallel pipelines do not cause write races.

**Why this priority**: Parallel execution in development pipelines can cause data loss or log truncation if write operations overlap.

**Independent Test**: Verified by spawning multiple concurrent processes attempting to update the feature state and proving that file locks serialize the operations and prevent corruption.

**Acceptance Scenarios**:

1. **Given** a write operation is in progress by process A, **When** process B attempts to transition state, **Then** process B is queued or blocked until process A completes, ensuring atomic updates.
2. **Given** concurrent CLI invocations, **When** all processes exit, **Then** the audit log hash chain remains continuous and uncorrupted.

---

### User Story 3 - Crash Consistency & Recovery Verification (Priority: P2)

As a **Prime** agent, I want the system to verify that the active state file matches the audit trail on boot, so that unexpected crashes or manual file modifications are immediately detected.

**Why this priority**: Detects any out-of-band manipulation or partial writes before the kernel executes new transitions.

**Independent Test**: Verified by manually editing state file values or truncating log entries and confirming the startup bootstrap checks fail.

**Acceptance Scenarios**:

1. **Given** the state file matches the last transition in the audit log, **When** the bootstrap validator runs, **Then** the system starts normally.
2. **Given** the state file deviates from the audit log (e.g. state is set to COMPLETED but audit log ends at PLANNING), **When** bootstrap validator runs, **Then** the system raises a validation exception and halts.

---

## Edge Cases

- **Partial Write / Crash mid-transaction**: What happens if the process is terminated while writing to the audit log or state file?
  - *Resolution*: The transactional layer must rollback or detect the partial block, raising an integrity failure on next boot.
- **Concurrent Veto and Approval**: What happens if Auditor vetoes a gate while another process attempts to approve it?
  - *Resolution*: Concurrency lock ensures the first write commits first. The subsequent write must fail because the state transition preconditions (gate validation active) are invalidated by the veto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST verify evidence signatures using **ECDSA P-256 with SHA-256** signatures, verified against the public keys stored in the Agent Registry.
- **FR-002**: The verification layer MUST remain **algorithm-agnostic** to allow future cryptographic agility.
- **FR-003**: The system MUST use a dedicated **CryptoVerifier** abstraction; evidence objects MUST delegate verification rather than containing verification logic.
- **FR-004**: The system MUST use file-system-level transactional locks (such as flock or exclusive OS locks) to synchronize multi-process access to state and log files.
- **FR-005**: The locking model MUST specify exclusive write semantics, timeout behavior (5 seconds), retry policy (every 100ms), and stale lock recovery.
- **FR-006**: The system MUST perform startup verification checking that the active feature state matches the last logged transition.
- **FR-007**: The system MUST implement atomic write commits (using temporary file $\rightarrow$ fsync $\rightarrow$ atomic rename) to prevent partial corruption of JSON lines logs and state files.
- **FR-008**: The agent key model MUST support metadata required for lifecycle management (key identifier, algorithm, status, creation metadata, rotation/version support).

### Key Entities

- **CryptoVerifier / CryptoProvider**: The abstract layer responsible for performing signature verification based on key metadata, decoupled from evidence models.
- **Agent Key Metadata**: Extended metadata attributes representing key status, version, and parameters.
- **Transactional Lock**: The OS-level mechanism ensuring exclusive write access during updates to `state.json` and `audit.jsonl`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of forged cryptographic signatures are rejected.
- **SC-002**: Zero (0%) state file corruptions occur when executing 10 concurrent CLI invocations.
- **SC-003**: System startup validation latency remains under 50ms.
- **SC-004**: 100% of out-of-sync state modifications (state file drifting from audit log) are detected on boot.
- **SC-005**: 100% of disabled, rotated, or expired keys fail validation.

## Assumptions

- Operating system supports lock operations on local directories.
- Cryptographic keys are distributed out-of-band to agents securely.
- Only local file storage is required for this phase.
