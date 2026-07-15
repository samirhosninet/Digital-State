# Walkthrough: Native Hermes Behavioral Alignment (feat-008)

This document details the behavioral alignment of Digital State governance inside the native Hermes execution and orchestration model.

## 1. Native Hermes Orchestration Workflow

The E2E workflow operates as a native extension of the Hermes agent lifecycle:
1. **User Goal / Objective Received:** Handled by the orchestrator profile (`prime`).
2. **SpecKit Generation:** Automatically creates specification (`spec.md`), implementation plan (`plan.md`), and tasks list (`tasks.md`).
3. **Kanban Task Creation:** A native SQLite-backed task is generated automatically via the CLI (`hermes kanban create`).
4. **Task Decomposition:** The task is decomposed natively (`hermes kanban decompose`) into child tasks or promoted directly to the `todo` lane.
5. **Execution in Workspace:** Work is routed to worker profiles (e.g., `builder` or `default`) executing in the assigned workspace.
6. **Digital State Governance Enforcement:** Every gate transition is cryptographically verified against ECDSA P-256 signatures of the respective agents.
7. **Task Completion & Sign-off:** Completed tasks are marked done natively, transitioning the state to `COMPLETED` on approval by `prime`.

---

## 2. Integrated Execution Logs

### A. Task Decomposition Event
```text
Specified t_b2716e8b → todo (no fanout) — retitled: 'Define and align native Hermes agent behavior'
```

### B. Kanban Board List State
```text
✓ t_3d9dc81b  done      builder               TASK-003: Native Hermes runtime integration
✓ t_15ee8728  done      prime                 TASK-004: Validate E2E Orchestration
⊘ t_9c021899  blocked   builder               TASK-005: Validate E2E Autonomous Execution
▶ t_f6730076  ready     prime                 TASK-006: Self-Governed Workspace Validation
✓ t_38ba7ad8  done      default               TASK-007: Implement Digital State feature
✓ t_c5e42822  done      default               Spec Digital State feature requirements
✓ t_984522fd  done      default               Implement Digital State core logic
✓ t_0b71b602  done      default               Expose Digital State via API
✓ t_74d505b9  done      default               Test Digital State feature
✓ t_b2716e8b  done      default               Define and align native Hermes agent behavior
```

### C. Digital State Verification Record (feat-008)
```json
{
  "feature_states": {
    "feat-008": "COMPLETED"
  },
  "gate_validations": {
    "feat-008": {
      "SPECIFICATION": true,
      "PLANNING": true,
      "TASKS": true,
      "IMPLEMENTATION": true,
      "VERIFICATION": true
    }
  }
}
```

---

## 3. Native Hermes Architectural Boundaries

Through runtime execution, the following three core boundaries imposed by the native Hermes Agent architecture were identified:

1. **Interactive/Operator Role Restriction (Terminal Lane):**
   * **Boundary:** The Hermes Kanban dispatcher does not spawn background workers for coordinator/reviewer profiles (`prime` and `auditor`). 
   * **Evidence:** Running the dispatcher skips the task with:
     `Skipped (non-spawnable assignee — terminal lane, OK): t_f6730076`
   * **Impact:** Prime must drive orchestration interactively or via CLI triggers; it cannot execute as an autonomous spawned background subprocess.

2. **Ephemeral Sandbox Workspace Isolation:**
   * **Boundary:** Spawns run in ephemeral workspaces (`workspace_kind: scratch`) which do not inherit parent environment variables like `no_proxy`.
   * **Evidence:** Worker runs crash with proxy-parsing errors on Windows unless environment variables (e.g. `no_proxy`) are explicitly cleared or managed.
   * **Impact:** Ephemeral sandboxes require explicit path and environment control to maintain networking connectivity to model endpoints.

3. **Cryptographic Key Isolation:**
   * **Boundary:** Real ECDSA signatures require private keys which are stored securely offline (in `.specify/keys/`). Ephemeral sandboxes do not mount or inherit these keys.
   * **Evidence:** Workers cannot sign evidence or approve transitions autonomously. Approvals must be signed by the human operator.
   * **Impact:** Digital State enforces secure human-in-the-loop validation for all gate approvals.
