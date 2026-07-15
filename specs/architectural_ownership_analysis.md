# Architectural Ownership Analysis: Minimizing the Governance Kernel

This document evaluates the architectural ownership of core governance capabilities against native Hermes capabilities to reduce duplication and achieve a minimal governance footprint.

## 1. Capabilities Ownership Evaluation

### A. Audit Logging
1. **Hermes Plugin/Hook:** Yes, plugin hooks (`on_session_start`, `on_session_end`, `post_tool_call`) can capture all execution events.
2. **Kanban Lifecycle:** Yes, logs can be bound to native task events (`task_events` table).
3. **Hermes Toolsets:** No, requires runtime hook interception.
4. **Task Metadata:** No, audit logs are a sequential cross-task ledger.
5. **Single Source of Truth:** Yes, events can write to native task logs.
* **Reclassification:** **Hermes extension** (observe and log events via plugin hooks).

### B. Evidence Submission
1. **Hermes Plugin/Hook:** Yes, hooks can collect artifact paths and outputs.
2. **Kanban Lifecycle:** Yes, files can be attached as task comments or metadata.
3. **Hermes Toolsets:** Yes, custom tools like `submit_evidence` can be exposed to the agent.
4. **Task Metadata:** Yes, stored inside the SQLite task run tables (`task_runs.metadata`).
5. **Single Source of Truth:** Yes, avoids redundant files by using the database.
* **Reclassification:** **Hermes extension** (implemented via custom tools/hooks).

### C. Gate Approvals & Policy Engine
1. **Hermes Plugin/Hook:** Yes, hooks (`pre_tool_call`) can block actions if policies are unmet.
2. **Kanban Lifecycle:** Yes, the dispatcher can block task promotion based on gate status.
3. **Hermes Toolsets:** No.
4. **Task Metadata:** No.
5. **Single Source of Truth:** Yes.
* **Reclassification:** **Hermes extension** (middleware hooks evaluating validation constraints).

### D. State Management
1. **Hermes Plugin/Hook:** Yes.
2. **Kanban Lifecycle:** Yes, task statuses (`triage`, `todo`, `ready`, `running`, `done`) map directly to feature states.
3. **Hermes Toolsets:** No.
4. **Task Metadata:** Yes, state maps directly to parent/child dependencies.
5. **Single Source of Truth:** Yes, deprecates `state.json` to query native database.
* **Reclassification:** **Hermes extension** (mapped directly to native task states).

---

## 2. Retained Governance Capabilities

### Cryptographic Validation (ECDSA P-256 Verification)
* **Why Hermes Cannot Own It:** Hermes profiles do not have a built-in cryptographic PKI/ECDSA engine to verify public/private key pairs and mathematically prove the authenticity of signed payloads.
* **Hermes Extension Points Evaluated:** 
  1. *Profile Configs:* Evaluated for storing keys. Insufficient because they lack verification algorithms.
  2. *Session Contexts:* Evaluated for passing identity. Insufficient because they pass unstructured key IDs, not verifying cryptographic signature byte payloads.
* **Architectural Cost of Keeping it Outside:** Requires maintaining the agents key registry (`agents.json`) and verification helpers inside the Digital State package.
* **Architectural Cost of Moving it Inside:** Requires modifying core Hermes profile systems to support PKI, asymmetric key management, and cryptographic signers.
