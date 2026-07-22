# FEATURE SPECIFICATION: ORCHESTRATION-003 — RUNTIME WORKFLOW AUTOMATION LAYER

**FEATURE ID:** ORCHESTRATION-003  
**TITLE:** Runtime Workflow Automation Layer  
**GOVERNANCE BASELINE:** ORCHESTRATION-002 (`9e6e96067786265f5556bbf45c3aa1e65d4c0f8e`)  
**STATUS:** SPECIFICATION ONLY (DESIGN PHASE)  

---

## 1. Executive Overview

ORCHESTRATION-003 defines the architecture for an automated **Runtime Workflow Automation Layer**. While ORCHESTRATION-002 established fail-closed security gates that block unauthorized Builder tool calls, ORCHESTRATION-003 automates the sequential execution of lifecycle steps under Prime authority.

The complete automated execution pipeline is:

$$\text{User Request} \longrightarrow \text{Prime Controller} \longrightarrow \text{Spec Kit Workflow} \longrightarrow \text{Kanban Card} \longrightarrow \text{Gate Check} \longrightarrow \text{Hermes Dispatcher} \longrightarrow \text{Builder Execution} \longrightarrow \text{Auditor Verification} \longrightarrow \text{Prime Approval} \longrightarrow \text{COMPLETED}$$

---

## 2. Component Responsibilities

### 2.1 Prime Runtime Controller (`PrimeRuntimeController`)
- **Location:** `src/digital_state/core/orchestrator.py`
- **Responsibilities:**
  1. Intercept user feature requests when Prime identity is active.
  2. Automate sequential Spec Kit workflow execution (`speckit.specify` $\rightarrow$ `speckit.plan` $\rightarrow$ `speckit.tasks`).
  3. Validate pre-orchestration phase approvals (`SPECIFICATION = True`, `PLANNING = True`, `TASKS = True`).
  4. Trigger Kanban Card Generator to emit task cards into `.specify/kanban.json`.

### 2.2 Hermes Dispatcher (`HermesDispatcher`)
- **Location:** `src/digital_state/hermes/dispatcher.py`
- **Responsibilities:**
  1. Receive task assignment events from `PrimeRuntimeController`.
  2. Evaluate `validate_builder_execution_gate(feature_id, builder_key)`.
  3. Dispatch execution context to Builder agent if and only if gate returns `(True, "Execution authorization gate passed.")`.
  4. Collect Builder implementation evidence upon completion.
  5. Route evidence to Auditor for verification (`verify_evidence`).
  6. Present verified evidence to Prime for final completion approval (`approve_completed`).

### 2.3 Kanban Generation Lifecycle (`KanbanManager`)
- **Location:** `src/digital_state/sdk/kanban.py`
- **Responsibilities:**
  1. Persist and manage `.specify/kanban.json`.
  2. Schema definition:
     ```json
     {
       "cards": {
         "<feature_id>": {
           "feature_id": "<feature_id>",
           "task_id": "TASK-001",
           "title": "<Task Title>",
           "assigned_to": "builder-agent",
           "status": "ASSIGNED",
           "prerequisites": ["spec.md", "plan.md", "tasks.md"]
         }
       }
     }
     ```
  3. State transitions: `BACKLOG` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `VERIFYING` $\rightarrow$ `COMPLETED`.

---

## 3. Failure States & Recovery Handlers

| Failure Event | Detection Point | Action & Result |
|---|---|---|
| **Missing Spec Kit Artifact** | `validate_builder_execution_gate()` | **Fail-Closed Block:** Execution halts; state remains at unapproved phase. |
| **Unapproved Prime Gate** | `validate_builder_execution_gate()` | **Fail-Closed Block:** Hermes returns `action: block` ("Prime pre-orchestration incomplete"). |
| **Missing Kanban Assignment** | `validate_builder_execution_gate()` | **Fail-Closed Block:** Hermes returns `action: block` ("Missing approved implementation assignment."). |
| **Auditor Verification Rejection** | `validate_gate_approval()` | **Transition Blocked:** State reverts to `IMPLEMENTATION`; defect report attached. |

---

## 4. Evidence Requirements

Every automated workflow transition must emit an immutable evidence entry into `audit_log.jsonl`:

1. `SPECIFICATION_AUTOMATED`: Emitted when `.specify/spec.md` is generated and approved.
2. `PLANNING_AUTOMATED`: Emitted when `.specify/plan.md` is generated and approved.
3. `TASKS_AUTOMATED`: Emitted when `.specify/tasks.md` is generated and approved.
4. `KANBAN_CARD_CREATED`: Emitted when `.specify/kanban.json` receives card assignment.
5. `BUILDER_DISPATCH_APPROVED`: Emitted when `validate_builder_execution_gate()` evaluates `True`.
6. `AUDITOR_VERIFIED`: Emitted when Auditor approves implementation evidence.
7. `PRIME_COMPLETED`: Emitted when Prime grants final completion approval.
