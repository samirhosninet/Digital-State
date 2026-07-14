# Digital State Architecture Specification

This document defines the architectural design, layers, and execution boundaries of the **Digital State Governance Framework**.

---

## 1. Architectural Layers & Namespace Layout

The codebase is structured under the `digital_state` namespace to maintain clean execution boundaries:

```text
+--------------------------------------------------------------+
|                       Governance Layer                       |
|           CONSTITUTION_v1.md & evidence_index.json           |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                       Framework Layer                        |
|            /framework/ interfaces (Runtime base)             |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                 digital_state Namespace Package              |
|                                                              |
|  ├── core/   (Core validation, registry, & lifecycle)        |
|  ├── sdk/    (Stable programmatic API interfaces)            |
|  ├── cli/    (Standalone CLI wrapper commands)               |
|  └── hermes/ (Stateless Hermes adapter & thin bridge plugin) |
+--------------------------------------------------------------+
```

---

## 2. Core Subsystems (`digital_state.core`)

The Core subsystem coordinates six decoupled engines:

1. **Agent Registry**: Houses identity keys and permission capabilities for registered agent profiles (`Prime`, `Builder`, `Auditor`).
2. **Policy Engine**: Evaluates permission contexts and checks authorization rules loaded from `policies.json`.
3. **Contract Engine**: Validates evidence structures against declarative contracts loaded from `lifecycle.json` or specs.
4. **Lifecycle Engine**: Coordinates transitions across lifecycle gates, persisting state changes atomically in `state.json`.
5. **Audit Logger**: Appends transitions and decisions to a cryptographically hash-chained, sequential JSON lines ledger.
6. **CryptoVerifier**: Decouples signature validations, executing ECDSA P-256 (SHA-256) signature verification over submitted payloads.
7. **FileLock**: Transactional concurrency locking manager that serializes multi-process writes.

---

## 3. Division of Responsibilities: Digital State vs. Hermes

Digital State is **not** an orchestrator. It does not manage agent tasks, scheduling, or runtime loops.

```text
User Request
     │
     ▼
Prime Agent (Hermes Runtime) ──(Kanban Orchestrator)──> Creates/Links Tasks
                                                               │
                                                               ▼
                                                       Builder / Auditor
                                                               │
                                                               ▼
                                                      Digital State SDK
                                                               │
                                                               ▼
                                                      Governance Decision
                                                       (ALLOW / DENY)
```

### A. Hermes Runtime Layer (Execution & Orchestration)
Hermes owns the operational workspace and scheduling:
* **Kanban Board & Tasks:** Tracking task creation, updates, and links via `kanban_create`, `kanban_link`, `kanban_comment`, and `kanban_complete`.
* **Agent Loops:** Invoking tools, managing active agent sessions, and executing handoffs between agents (e.g. Prime assigning work to Builder).
* **Profiles:** Managing runtime local keys and configurations.

### B. Digital State Layer (Governance Authority)
Digital State evaluates compliance and security boundaries:
* **Identity Verification:** Validating that request signatures match registered public keys.
* **Authority Verification:** Ensuring the requesting agent has permissions for the current gate.
* **Policy Evaluation:** Enforcing constitutional rules and constraints.
* **Audit Ledger:** Recording every allowance and denial in the immutable ledger.
* **Bridge Plugin:** The `digital_state.hermes.plugin` is a **stateless runtime bridge**. It intercepts actions via `pre_tool_call` hooks and queries the SDK for `ALLOW` / `DENY` decisions, but does not participate in Kanban orchestration.

---

## 4. Continuous Integration

The repository includes a GitHub Actions CI pipeline (`.github/workflows/governance-ci.yml`) that runs the full test suite on push to `main` and all pull requests, validating that every change meets the established governance rules.
