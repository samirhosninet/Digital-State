# Behavioral Audit Matrix: Digital State vs. Native Hermes Architecture

This audit assesses the alignment of Digital State capabilities with native Hermes agent features, highlighting areas of reuse, extension points, and unique governance requirements to eliminate duplicate implementation.

## 1. Capability Classification Matrix

| Capability | Classification | Description & Native Hermes Reference |
| :--- | :--- | :--- |
| **SpecKit orchestration** | **Hermes extension** | Driven by user prompt context, but tracked via Digital State plugin hooks (`on_session_start`, `pre_tool_call`) which verify the creation and integrity of specification/planning artifacts. |
| **Kanban orchestration** | **Native Hermes capability** | SQLite-backed task board (`kanban.db`) and task actions (`create`, `list`, `complete`, `show`) are native features of `hermes_cli.kanban`. |
| **Task decomposition** | **Native Hermes capability** | Decomposing triage tasks into child task dependency graphs is handled by `hermes kanban decompose`. |
| **Task routing** | **Native Hermes capability** | Assignment of tasks to named profiles (`builder`, `prime`, `auditor`) and routing them to target workspaces is managed natively by Kanban. |
| **Dispatcher interaction** | **Native Hermes capability** | Background polling, stale task reclamation, and worker subprocess spawning is executed by `hermes kanban dispatch`. |
| **Workspace management** | **Native Hermes capability** | Ephemeral workspace scratch directories and isolated git worktrees are provisioned by native Kanban workspace dispatchers. |
| **Agent lifecycle** | **Hermes extension** | Session hook hooks (`on_session_start`, `on_session_end`, `pre_llm_call`) intercept the worker runs to query gate authorization. |
| **Audit logging** | **Digital State capability** | Cryptographically chained historical transaction logging (`audit_log.jsonl`) to guarantee immutable execution records. |
| **Evidence submission** | **Digital State capability** | Explicit submissions of verifiable gate evidence contents by different agents to `.specify/`. |
| **Gate approvals** | **Digital State capability** | Evaluation of policy engine constraints against submitted evidence before permitting phase transitions. |
| **State management** | **Digital State capability** | Central state tracking database (`state.json`) containing active states of features across the workspace. |
| **Cryptographic validation** | **Digital State capability** | Authentication of profile signatures (ECDSA P-256) using public keys configured in `agents.json`. |

---

## 2. Elimination of Duplicated Responsibilities

To minimize the Digital State footprint and prevent duplication:

1. **Rely Natively on `kanban.db` State:**
   * *Problem:* Digital State could duplicate checklist status tracking.
   * *Solution:* Remove independent checklist checkers from the kernel and read the native SQLite `tasks` status (`status='done'`) directly to verify gate implementation.
2. **Deprecate Custom Workspace Setup:**
   * *Problem:* Early kernel utilities had options to create temporary folders or checkout branches.
   * *Solution:* Fully deprecate these paths and rely entirely on the native environment `TERMINAL_CWD` and `workspace` paths populated by the Hermes dispatcher.
3. **Harmonize Profile Key Resolution:**
   * *Problem:* `agents.json` duplicates user profile identity mapping.
   * *Solution:* Query Hermes profile configurations (`~/.hermes/profiles/`) directly to extract public key credentials when Hermes identity federation is enabled, rather than maintaining a separate keys database.
