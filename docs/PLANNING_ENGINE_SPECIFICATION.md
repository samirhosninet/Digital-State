# PLANNING ENGINE SPECIFICATION — PRIME ARCHITECTURE ENGINE

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Planning Engine Principles

The **Planning Engine** inside Prime enforces mathematical dependency ordering, architectural scoping, and design verification before any worker agent is dispatched.

---

## 2. Planning Protocol Rules

```text
               ┌────────────────────────────────────────┐
               │         SPECIFICATION INPUT            │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │    COMPONENT DEPENDENCY GRAPH ENGINE   │
               │ • Dependency Layer Ordering            │
               │ • File Boundary Mapping                │
               │ • Test Plan Construction               │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │        PRIME ARTIFACT REVIEW GATE       │
               │ [PASS] ──► Kanban Generation           │
               │ [FAIL] ──► Regenerate / Clarify        │
               └────────────────────────────────────────┘
```

1. **Dependency Layering:** Components must be ordered strictly from underlying foundations upward (e.g. models $\rightarrow$ core logic $\rightarrow$ API bindings $\rightarrow$ CLI / UI).
2. **File Scope Demarcation:** Each planned modification must explicitly state file status:
   - `[MODIFY] file_path`
   - `[NEW] file_path`
   - `[DELETE] file_path`
3. **Verification Plan Requirement:** Every plan must include explicit automated verification commands (`pytest tests/ -v`, build commands) and manual verification criteria.

---

## 3. Prime Review Gate Evaluation Rules

During **Phase 3 (Prime Review Gate)**, Prime evaluates generated design artifacts against 4 criteria:

| Criterion | Evaluation Requirement | Failure Action |
| :--- | :--- | :--- |
| **Completeness** | All user stories in `spec.md` covered by tasks in `tasks.md`. | Re-run `speckit-tasks` |
| **Scope Isolation** | No task touches frozen core paths without authorization. | Re-run `speckit-plan` |
| **Test Coverage** | Automated test defined for every new feature component. | Re-run `speckit-plan` |
| **Consistency** | Zero contradiction between `plan.md` architecture and `tasks.md`. | Re-run `speckit-analyze` |
