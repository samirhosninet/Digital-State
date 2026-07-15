# Final Evidence Review & Technical Execution Paths

This document provides physical implementation paths, hook call locations, and migration criteria to substantiate the runtime claims of the Digital State architecture.

## 1. Fail-Closed Enforcement Path

The fail-closed block executes along a strict hook validation chain:

* **Trigger:** Plugin fails to load during registration or integrity verification (e.g. invalid `audit_log.jsonl` block hashes).
* **Code Location:** `src/digital_state/hermes/plugin.py:initialize` (returns `False`, leaving `self.is_loaded = False`).
* **Enforcement:** In `src/digital_state/hermes/plugin.py:pre_tool_call_handler` (lines 106-123):
  ```python
  if not self.is_loaded:
      logger.error("Digital State Plugin is not loaded. Fail-Safe Deny triggered.")
      return {
          "action": "block",
          "message": "Digital State Plugin is not loaded. Fail-Safe Deny triggered."
      }
  ```
* **Bypass Mitigation:** All Digital State–governed tool executions pass through the registered `pre_tool_call` hook.

---

## 2. Event Synchronization Protocol

* **Function:** `submit_evidence(feature_id, "tool_call", ...)` called in `plugin.py:post_tool_call_handler`.
* **Caller:** Native Hermes process runner on completion of tool executions.
* **Invocation Path:**
  `Hermes Tool Finished` -> `plugin.py:post_tool_call_handler` -> `sdk/api.py:submit_evidence` -> `core/engine.py:submit_evidence`.
* **Execution Model:** **Synchronous and Event-Driven**. Hook execution pauses until verification database updates are persisted in `state.json`.

---

## 3. State & Ledger Recovery Status

* **Status:** **PLANNED**.
* **Reconstruction Strategy:** State reconstruction by traversing the cryptographically signed events log `audit_log.jsonl` and building the `state.json` cache is planned for the next feature release milestone. The current `repair` command validates the physical layout of files.

---

## 4. Open Migration Items Status

### A. DS-MIG-001 (Agent Identity Registry)
* **Current Implementation:** Key mappings are loaded from `.specify/agents.json`.
* **Target Implementation:** Resolve public keys natively from Hermes profiles directory (`~/.hermes/profiles/<profile_name>/`).
* **Blocking Dependency:** Hermes profile configuration schema currently supports name and workspace paths, but lacks options to register public key certificates.
* **Completion Criteria:** Profile settings schema updated to support agent public key parameters.

### B. DS-MIG-002 (Feature Lifecycle State)
* **Current Implementation:** Phases are mapped in `.specify/state.json`.
* **Target Implementation:** Transition states are stored directly as metadata tags in the native SQLite `kanban.db` schema.
* **Blocking Dependency:** Modifying `kanban.db` schema requires updates to native Hermes database adapters.
* **Completion Criteria:** Feature state metadata columns are natively exposed in `kanban.db` tables.
