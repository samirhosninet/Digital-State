# Digital State Governance Kernel

The Digital State Governance Kernel is a declarative, contract-driven, and policy-authorized governance operating layer. It coordinates specifications, technical plans, task lists, and verification results across multiple agent profiles, logging every state transition in a cryptographically hash-chained audit log.

---

## Architecture Overview

The system is decoupled into independent engines coordinated by the `GovernanceKernel`:

1. **Agent Registry**: Manages identities, roles (`Prime`, `Builder`, `Auditor`), verification keys, and operational statuses.
2. **Policy Engine**: Validates action requests against dynamic rule definitions loaded from [policies.json](file:///d:/Digital-State/src/governance/contracts/policies.json).
3. **Contract Engine**: Validates metadata structures using declarative contract rules (supporting `exists`, `gte`, `eq` operators).
4. **Lifecycle Engine**: Manages sequential phase transitions (`SPECIFICATION` $\rightarrow$ `PLANNING` $\rightarrow$ `TASKS` $\rightarrow$ `IMPLEMENTATION` $\rightarrow$ `VERIFICATION` $\rightarrow$ `COMPLETED`) with **on-disk state persistence** at `.specify/state.json`.
5. **Audit Logger**: Commits hash-chained, sequentially numbered JSONL log files tracking submissions, state shifts, and vetoes.

---

## Production Hardening Features

The Governance Kernel has been hardened with enterprise-ready parameters:

### 1. Production Cryptography
* **ECDSA P-256 (SHA-256)**: Signatures are validated using the elliptic curve SECP256R1 standard.
* **CryptoVerifier Abstraction**: A dedicated algorithm-agnostic verifier layer decoupling cryptography validations from the underlying data models.
* **Metadata Schema**: Agent keys are tracked with versioning, algorithms, creation timestamps, and active status fields.

### 2. Transactional Concurrency Lock
* **Exclusive write locks**: Multiple concurrent processes are serialized using atomic directory-based file locking under `.specify/governance.lock`.
* **Lock Timings**: Acquisition attempts retry every 100ms and fail after a 5-second timeout.
* **Stale Lock Recovery**: Dead PID ownership is checked during acquisition and stale locks are automatically cleared.

### 3. Atomic File Writes
* **Crash-safe updates**: Log appends and state updates write to temporary files, commit using `os.fsync()`, and perform atomic renames (`os.replace`) to target paths.

### 4. Crash Recovery Bootstrap
* **Boot checks**: Bootstrap validator checks state-to-log alignment on initialization, halting if state drift or truncation is detected.

---

## User Installation Journey

Transform the repository into an operational workspace with a single execution path:

```text
Clone Repository
      │
      ▼
Run Installer (install.ps1 / install.sh)
      │
      ▼
Digital State Bootstrap (digitalstate init)
      │
      ▼
Verify Installation (digitalstate doctor)
      │
      ▼
Ready State (Governance Active)
```

### Setup Steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/samirhosninet/Digital-State.git
   cd Digital-State
   ```

2. **Run the Installer:**
   - **Windows (PowerShell):**
     ```powershell
     powershell -ExecutionPolicy Bypass -File install.ps1
     ```
   - **Linux/macOS (Bash):**
     ```bash
     chmod +x install.sh
     ./install.sh
     ```

   *The installer validates Python >= 3.11, installs package dependencies, and automatically initializes the workspace.*

3. **Verify Installation:**
   Run the verification diagnostics tool:
   - **Windows:**
     ```powershell
     .venv\Scripts\digitalstate doctor
     ```
   - **Linux/macOS:**
     ```bash
     ./.venv/bin/digitalstate doctor
     ```

---

## CLI Usage Command Schema

The standalone command interface wraps the governance kernel:

### 1. Register Agent
```powershell
digitalstate register --id <agent_id> --role <role> --key <key>
```

### 2. Status Check
```powershell
digitalstate status --feature <feature_id>
```

### 3. Submit Evidence
```powershell
digitalstate submit --feature <feature_id> --gate <gate> --evidence '<json_string>' --agent <agent_id>
```
*Note: The `--evidence` string must contain a valid `"signature"` field matching the agent's registration key.*

### 4. Approve Checkpoint
```powershell
digitalstate approve --feature <feature_id> --gate <gate> --agent <agent_id>
```

### 5. Veto Checkpoint
```powershell
digitalstate reject --feature <feature_id> --gate <gate> --reason <reason> --agent <agent_id>
```

---

## Verification Testing

Run all unit and integration test suites:
```powershell
$env:PYTHONPATH="D:\Digital-State\src;D:\Digital-State"; uv run python -m pytest tests/ -v
```
* **Success Rate**: **100% Pass** (44 tests verifying baseline, concurrency locks, ECDSA validation, recovery, and Hermes plugin flows).

---

## Security

See [SECURITY.md](SECURITY.md) for the security policy, known security boundaries, and migration guidance.

---

## Integration Layer (Mock Hermes Boundary)

> [!WARNING]
> **Hermes Integration Boundary:** The Hermes client runtime integration layer at `integrations/hermes/` is currently a **mock/simulation implementation**. It does not establish connectivity to a live, production-deployed remote Hermes execution cluster. 

The integration supports:
- Stateless plugin loading and lifecycle hook orchestration (`on_session_start`, `pre_llm_call`, `post_llm_call`, `pre_tool_call`, `post_tool_call`, `on_session_end`).
- Simulated in-memory session run loops for local test and policy validation.

For developer details on the mock contracts, see the [Hermes integration contract specification](file:///d:/Digital-State/integrations/hermes/README.md).
