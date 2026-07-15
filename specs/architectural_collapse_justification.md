# Architectural Collapse Justification: Domain Layer Separation

This document justifies the separation of the core domain layer (`src/digital_state/core/`) from the Hermes plugin bridge (`src/digital_state/hermes/plugin.py`) based on modularity, testability, and reuse guidelines.

## 1. Domain Library vs. Plugin Bridge Separation

The native Hermes plugin model recommends decoupling the bridge (hooks, slash commands, tool specifications) from the domain execution library:

```text
  [Hermes Agent Runtime]
          │
          ▼ (Plugin Lifecycle Bridge)
  [src/digital_state/hermes/plugin.py]
          │
          ▼ (SDK Abstraction Layer)
  [src/digital_state/sdk/api.py]
          │
          ▼ (Domain Logic Library)
  [src/digital_state/core/*]
```

---

## 2. File-by-File Ownership & Justification Analysis

| File Path under `src/digital_state/core/` | Purpose & Responsibility | Merging to `plugin.py` Feasibility | Modularity, Testing & Reuse Impact |
| :--- | :--- | :--- | :--- |
| **`verifier.py`** | Executes ECDSA P-256 key loading and cryptographic verification. | **NO** | Allows standalone cryptographic unit testing (`tests/unit/test_verifier.py`) without initializing a mock Hermes plugin context. |
| **`evidence.py`** | Models gate evidence objects and binds verification signatures. | **NO** | Permits evidence parsing, construction, and serialization during test and mock stages. |
| **`audit.py`** | Implements the SHA-256 chained ledger append logic for `audit_log.jsonl`. | **NO** | Shared across the plugin hooks and the standalone command line interface CLI (`cli.py`). |
| **`policy.py`** | Evaluates policy rules and matches profile assignees. | **NO** | Keeps rules evaluation decoupled from Hermes session configurations. |
| **`lifecycle.py`** | Traces gate validations and updates state mapping databases. | **NO** | Keeps state.json transition logic independent of specific Hermes runtime states. |
| **`contracts.py`** | Loads and validates schemas inside `core/contracts/`. | **NO** | Allows loading schemas dynamically from local workspace paths. |
| **`locking.py`** | Implements cross-process file-level concurrency locks. | **NO** | Reused by CLI and plugin execution threads to prevent transaction corruption. |
| **`config.py`** | Resolves relative directory paths and configurations. | **NO** | Shared by all CLI, SDK, and plugin modules to locate the `.specify/` root. |
| **`bootstrap.py`**| Validates structural directory configurations at startup. | **NO** | Run once during CLI repair or initial plugin loading. |
| **`exceptions.py`**| Custom domain-level exceptions (RegistryError, LifecycleError). | **NO** | Imports easily across all components without circular reference risks. |

---

## 3. Core Architectural Justifications

1. **Standalone Testability:** Domain components can be fully validated via standard unit test tools without spawning Hermes subprocesses or mocking profile variables.
2. **Preventing Circular Import References:** The CLI (`cli.py`) needs to parse arguments and run repairs without importing the Hermes agent library itself.
3. **Preventing Code Bloat:** Merging all validation, crypto, and locking logic into `plugin.py` would result in a massive single-file module (4,000+ lines), degrading maintainability.
