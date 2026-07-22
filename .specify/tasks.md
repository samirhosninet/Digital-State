# TASK BREAKDOWN: ORCHESTRATION-003 — RUNTIME WORKFLOW AUTOMATION LAYER

**FEATURE ID:** ORCHESTRATION-003  
**TITLE:** Runtime Workflow Automation Layer  
**GOVERNANCE BASELINE:** ORCHESTRATION-002 (`9e6e96067786265f5556bbf45c3aa1e65d4c0f8e`)  
**STATUS:** SPECIFICATION ONLY (TASKS PHASE)  

---

## Task Matrix & Dependency Order

| Task ID | Component / File | Description | Prerequisites | Status |
|---|---|---|---|---|
| **TASK-001** | `src/digital_state/sdk/kanban.py` | Implement `KanbanManager` for reading, writing, and validating `.specify/kanban.json` cards. | None | **SPECIFIED** |
| **TASK-002** | `src/digital_state/core/orchestrator.py` | Implement `PrimeRuntimeController` to execute sequential Spec Kit workflow (`speckit.specify` $\rightarrow$ `plan` $\rightarrow$ `tasks`). | TASK-001 | **SPECIFIED** |
| **TASK-003** | `src/digital_state/hermes/dispatcher.py` | Implement `HermesDispatcher` for gated Builder dispatch after `validate_builder_execution_gate()` approval. | TASK-002 | **SPECIFIED** |
| **TASK-004** | `src/digital_state/hermes/plugin.py` | Integrate `PrimeRuntimeController` and `HermesDispatcher` into Hermes plugin pre/post hooks. | TASK-003 | **SPECIFIED** |
| **TASK-005** | `tests/test_orchestration_automation.py` | Write comprehensive automated test suite verifying end-to-end runtime automation. | TASK-004 | **SPECIFIED** |
| **TASK-006** | Full Repository Test Suite | Execute complete pytest regression suite (158+ tests) to certify zero regressions. | TASK-005 | **SPECIFIED** |

---

## Detailed Task Specifications

### TASK-001: Implement `KanbanManager` (`src/digital_state/sdk/kanban.py`)
- Implement `KanbanManager` class.
- Methods: `create_card(feature_id, assigned_to, title)`, `get_card(feature_id)`, `update_card_status(feature_id, status)`.
- Write unit tests in `tests/test_kanban_manager.py`.

### TASK-002: Implement `PrimeRuntimeController` (`src/digital_state/core/orchestrator.py`)
- Implement `PrimeRuntimeController` class.
- Methods: `execute_pre_orchestration(user_request, feature_id)`, `verify_pre_orchestration_artifacts(feature_id)`.
- Ensure execution strictly checks Prime role permissions.

### TASK-003: Implement `HermesDispatcher` (`src/digital_state/hermes/dispatcher.py`)
- Implement `HermesDispatcher` class.
- Methods: `dispatch_builder(feature_id, builder_key)`, `submit_and_verify(feature_id, payload)`.
- Enforce call to `validate_builder_execution_gate()` prior to dispatch.

### TASK-004: Wire Hermes Plugin (`src/digital_state/hermes/plugin.py`)
- Connect `DigitalStatePlugin` handlers to `PrimeRuntimeController` and `HermesDispatcher`.
- Preserve Fail-Closed deny policy for unauthenticated tool calls.

### TASK-005 & TASK-006: Automated Verification & Certification
- Run `tests/test_orchestration_automation.py`.
- Run complete repository test suite to certify baseline stability.
