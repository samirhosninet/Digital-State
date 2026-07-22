# Architectural Decision Record: ADR-0001 — Audit & Governance Architecture Separation

**Status**: Accepted  
**Date**: 2026-07-22  
**Governing Directive**: DS-GOV-ADR-0001-ACCEPT  
**Supersedes/Refines**: DS-GOV-BOOTSTRAP-001  

---

## 1. Context & Problem Statement

During the execution of DS-GOV-BOOTSTRAP-001 (Builder Bootstrap Deadlock Resolution), the Builder profile reported complete implementation and 130/130 passing tests. However, independent auditor execution stalled because every tool invocation was blocked by the Digital State Governance Fail-Safe (`src/digital_state/hermes/plugin.py`):

```text
Missing signed agent key or feature ID metadata. Fail-Safe Deny triggered.
```

### Root Cause Analysis
The failure was traced to context coupling in `src/digital_state/runtime/adapter.py`:
- `RuntimeStore(root=ws_root)` was attempting to resolve the agent's identity (`registry/agents.json`) from the **Workspace Context** (`ws_root`).
- The authoritative agent registry and identity keys exist in the **Runtime Context** (`DIGITAL_STATE_HOME` or `%LOCALAPPDATA%\digital-state`), which is independent of the workspace repository.
- Because `ws_root` contained no registered runtime keys, `_governed_context()` returned `(None, None)`, and the fail-closed governance plugin correctly denied access.

This created an architectural deadlock:
```text
Implementation Complete
Independent Verification Blocked
```

To resolve this deadlock without compromising security, an authoritative architectural decision is required to formalize context separation and the independent audit model.

---

## 2. Decision: ACCEPTED

ADR-0001 is **ACCEPTED** as the governing audit and runtime architecture for Digital State.

### Core Architectural Principles & Invariants:

1. **Context Separation (Workspace vs. Runtime vs. Governance)**
   - **Workspace Context (`ws_root`)**: Source for repository code, `.specify/state.json`, and `feature_id`.
   - **Runtime Context (`resolve_runtime_root()`)**: Authoritative source for agent identity (`registry/agents.json`), identity keys, and persistent state stored at `DIGITAL_STATE_HOME` / `%LOCALAPPDATA%\digital-state`.
   - **Governance Context**: 3-tier resolved context passed to `validate_gate_approval()`.
   - `RuntimeStore()` must default to `resolve_runtime_root()`, maintaining strict decoupling between repository workspace directories and system agent identity stores.

2. **Immutable Fail-Closed Security Posture**
   - The fail-safe deny mechanism in `hermes/plugin.py` must **never** be bypassed, disabled, or suppressed during audit or bootstrap operations.
   - Any execution lacking valid `agent_key` or `feature_id` metadata must be blocked.
   - Independent verification must succeed by providing valid identity resolution via the Runtime Context, not by weakening security controls.

3. **Independent Audit Execution Model**
   - Independent Auditor sessions execute with `DIGITAL_STATE_HOME` pointed at an authorized Runtime Context containing provisioned Auditor (`auditor-agent`) credentials.
   - Audit verification must be reproducible from a clean environment without hardcoded workspace dependencies.

---

## 3. Consequences

### Positive
- **Resolves Audit Deadlock**: Enables Independent Auditors to execute verification tools under a fully provisioned Runtime Context while preserving gate-based governance.
- **Enforces Constitution Principles I & V**: Preserves absolute separation of governance and execution while ensuring Independent Verification without self-approval.
- **Hardens Fail-Closed Safety**: Guarantees that governance rules cannot be bypassed via temporary environment switches or mock permissive flags.

### Negative / Trade-Offs
- Requires test harnesses and audit tools to explicitly provision or resolve the Runtime Context (`DIGITAL_STATE_HOME`) when verifying features.

---

## 4. Repository Evidence Supporting Acceptance

1. **`src/digital_state/runtime/adapter.py`**: Refactored `RuntimeStore()` instantiation to decouple `ws_root` from runtime identity lookup.
2. **`tests/integration/test_tenant_isolation.py`**: Added explicit assertions verifying that `RuntimeStore` uses `resolve_runtime_root()`, preventing re-coupling.
3. **`tests/unit/test_plugin.py`**: `test_plugin_hooks_fail_safe_deny` continues to pass, proving fail-closed security remains 100% active.
4. **Test Suite Results**: 130 / 130 tests passing under standard test execution.

---

## 5. Compliance & References

- **Digital State Constitution**: Principles I (Separation of Governance/Execution), II (Role Segregation), IV (Gate-Based Progression), V (Independent Verification), Constraint 1 (Verifiable Identity).
- **AWS Prescriptive Guidance**: Architectural Decision Record (ADR) Process.
- **NIST SP 800-171 / CMS Configuration Management**: Formal Baseline & Governance Control.
