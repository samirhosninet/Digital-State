# Digital State Architecture Specification

This document defines the architectural design, layers, and execution flows of the **Digital State Governance Framework**.

---

## 1. Architectural Layers

The repository is decoupled into distinct boundaries to separate declarative interfaces, concrete execution code, and integration adapters:

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
|                         Kernel Layer                         |
|         /src/kernel/ execution logic & CLI controls          |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                      Integration Layer                       |
|             /integrations/hermes/ client adapter             |
+--------------------------------------------------------------+
```

---

## 2. Core Subsystems (Kernel Layer)

The concrete Governance Kernel coordinates six decoupled engines:

1. **Agent Registry**: Houses identity keys and permission capabilities for registered agent profiles (`Prime`, `Builder`, `Auditor`).
2. **Policy Engine**: Evaluates permission contexts and checks authorization rules loaded from `policies.json`.
3. **Contract Engine**: Validates evidence structures against declarative contracts loaded from `lifecycle.json` or specs.
4. **Lifecycle Engine**: Coordinates transitions across lifecycle gates, persisting state changes atomically in `state.json`.
5. **Audit Logger**: Appends transitions and decisions to a cryptographically hash-chained, sequential JSON lines ledger.
6. **CryptoVerifier**: Decouples signature validations, executing ECDSA P-256 (SHA-256) signature verification over submitted payloads.
7. **FileLock**: Transactional concurrency locking manager that serializes multi-process writes.

---

## 3. Integration Interface Boundaries

External agent runtimes (such as Hermes) do not run inside the kernel. Instead, they interact with the kernel through the standalone CLI or integration adapters that implement the `RuntimeCapability` declarative base interface.
This guarantees:
- Complete technology-agnostic runtime compatibility.
- Decoupled code execution context (kernel logic remains pure).
- Secure, signed evidence submissions.

> **Note**: The current Hermes adapter (`integrations/hermes/client.py`) is a **mock implementation**. It does not connect to a real Hermes instance. See `integrations/hermes/README.md` for the contract a real adapter must fulfill.

---

## 4. Continuous Integration

The repository includes a GitHub Actions CI pipeline (`.github/workflows/governance-ci.yml`) that runs the full test suite on every push to `main` and on all pull requests. This ensures no change merges without passing all governance verification tests.
