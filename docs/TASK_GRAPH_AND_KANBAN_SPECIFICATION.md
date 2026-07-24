# TASK GRAPH AND KANBAN GENERATION SPECIFICATION

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Executive Summary

This specification defines how `tasks.md` (generated during `speckit-tasks`) serves as the **canonical source of truth** for automatic Kanban board generation inside Digital State.

---

## 2. Kanban Compilation Schema

Prime parses `tasks.md` and materializes `.specify/kanban/board.json` using the following schema structure:

```json
{
  "$schema": "https://digitalstate.io/schemas/kanban.v2.json",
  "project_id": "DS-V2-PROJECT-001",
  "source_artifact": "tasks.md",
  "generated_at": "2026-07-24T06:57:00Z",
  "total_cards": 5,
  "columns": ["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"],
  "cards": [
    {
      "id": "TASK-001",
      "title": "Implement UserUpdater snapshot backup engine",
      "dependencies": [],
      "status": "DONE",
      "allowed_file_scope": [
        "src/digital_state/cli/updater.py",
        "tests/test_updater_experience.py"
      ],
      "acceptance_criteria": [
        "Creates .specify/.backup_pre_update directory snapshot",
        "Rolls back cleanly if migration fails",
        "Passes test_updater_experience.py"
      ],
      "assigned_agent": "builder-agent",
      "verifier_agent": "auditor-agent",
      "evidence_hash": "sha256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

---

## 3. Dependency Resolution & Dispatch Algorithm

```text
               ┌────────────────────────────────────────┐
               │    PARSE tasks.md & MAP DEPENDENCIES   │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │         EVALUATE UNBLOCKED CARDS       │
               │ Card dependencies ⊆ {DONE Cards}       │
               └───────────────────┬────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────┐
               │ DISPATCH HIGHEST PRIORITY TODO CARD    │
               │ Prime ──► Builder                      │
               └────────────────────────────────────────┘
```

1. **Unblocked Card Identification:** A card is unblocked if and only if all Card IDs listed in its `dependencies` array have status `DONE`.
2. **Deterministic Priority Dispatch:** Prime selects the first unblocked `TODO` card according to the original topological order in `tasks.md`.
3. **Single Active Execution Invariant:** Exactly ONE card may be in `IN_PROGRESS` or `IN_REVIEW` status across the entire system at any given moment.
