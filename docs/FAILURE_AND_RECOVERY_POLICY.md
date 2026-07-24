# FAILURE AND RECOVERY POLICY — PRIME OPERATING MODEL

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Executive Summary

This policy defines the **Failure & Recovery Contract** for Prime, Builder, and Auditor. It ensures that system interruptions, network disconnects, or unavailable tool calls never cause state corruption, data loss, or un-audited state transitions.

---

## 2. Tool Access & Interruption Recovery Protocol

```text
[Tool Failure / Interruption Event]
                 │
                 ▼
     1. Stop Execution Immediately
                 │
                 ▼
     2. Preserve Execution State (.specify/state.json)
                 │
                 ▼
     3. Preserve Evidence Log (.specify/memory/audit_log.jsonl)
                 │
                 ▼
     4. Record Exact Resume Point (.specify/resume_checkpoint.json)
                 │
                 ▼
     5. Report Blocking Condition
                 │
                 ▼
     [Recovery Detected] ──► Resume Automatically from Checkpoint
```

If tool access or environment execution is genuinely unavailable:
1. **Stop Execution:** Immediately halt active sub-agent tasks.
2. **Preserve Execution State:** Write current state machine status to `.specify/state.json`.
3. **Preserve Evidence Logs:** Ensure append-only audit log `.specify/memory/audit_log.jsonl` is flushed and sealed.
4. **Record Resume Checkpoint:** Save resume metadata to `.specify/resume_checkpoint.json` containing:
   - `phase`: Active phase name
   - `card_id`: Currently active Kanban card ID
   - `subagent`: Active subagent ID
   - `resume_step`: Exact line index / instruction step
5. **Report Blocking Condition:** Output structured diagnostic error detailing root cause.
6. **Auto-Resume:** Upon environment recovery, Prime automatically loads `.specify/resume_checkpoint.json` and resumes execution seamlessly.

---

## 3. Builder & Auditor Rollback Policy

- **Builder Task Failure:** If Builder encounters an unhandled exception or syntax failure, the active card is NOT marked `IN_REVIEW`. The card remains in `IN_PROGRESS` or is reset to `TODO` with the exception stack trace attached.
- **Auditor Verification Veto:** If Auditor detects failing unit tests or hash integrity mismatches during `AUDITOR_REVIEW`:
  1. Card state reverts from `IN_REVIEW` to `TODO`.
  2. Failure report is logged in `.specify/kanban/failures/` detailing exact test failures.
  3. Prime re-dispatches the card to Builder alongside Auditor's failure report.
  4. Work trees are rolled back to the last clean checkpoint before re-execution.
