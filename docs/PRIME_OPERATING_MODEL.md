# PRIME OPERATING MODEL — ARCHITECTURE SPECIFICATION

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Overview & Single-Endpoint Architecture

The **Prime Operating Model** establishes Prime as the **sole public interface and orchestration entry point** for all engineering project requests within Digital State.

Users do not manually execute individual SpecKit stages or communicate directly with worker agents (Builder or Auditor). Instead, Prime orchestrates the end-to-end engineering lifecycle through an automated, 8-phase state machine.

```text
                               ┌───────────────────────────┐
                               │           USER            │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │           PRIME           │
                               │   (Single Orchestration   │
                               │    & User Endpoint)       │
                               └─────────────┬─────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
┌─────────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│     SPECKIT PIPELINE        │ │  AUTOMATIC KANBAN ENGINE  │ │  WORKER AGENT DISPATCH    │
│ Phase 1: Intent Analysis    │ │ Phase 4: Kanban Gen       │ │ Phase 5: Builder Dispatch │
│ Phase 2: Pipeline Execution │ │ • Parse tasks.md          │ │ Phase 6: Auditor Verification
│ Phase 3: Prime Review Gate  │ │ • Track Card Status Flow  │ │ Phase 7-8: Continuous Loop│
└─────────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
```

---

## 2. The 8-Phase Lifecycle State Machine

### **Phase 1 — Intent Analysis**
- Prime analyzes user prompts and objectives.
- Identifies underspecified requirements, missing assumptions, or technical ambiguities.
- If information is missing, Prime invokes the clarification protocol before any architecture or task planning begins.

### **Phase 2 — SpecKit Automated Pipeline**
Prime sequentially executes the 6 SpecKit workflow stages without requiring manual command execution:
1. `speckit-specify` $\rightarrow$ Generates feature specification (`spec.md`).
2. `speckit-clarify` $\rightarrow$ Encodes targeted clarifications if needed (`spec.md` update).
3. `speckit-plan` $\rightarrow$ Generates architecture design (`plan.md`).
4. `speckit-checklist` $\rightarrow$ Generates quality acceptance criteria (`checklist.md`).
5. `speckit-tasks` $\rightarrow$ Generates dependency-ordered actionable tasks (`tasks.md`).
6. `speckit-analyze` $\rightarrow$ Performs non-destructive cross-artifact consistency analysis across `spec.md`, `plan.md`, and `tasks.md`.

### **Phase 3 — Prime Review Gate**
- Prime evaluates all generated design artifacts against quality, completeness, and consistency criteria.
- If artifacts fail validation, Prime automatically regenerates or requests targeted clarification instead of proceeding to code execution.

### **Phase 4 — Automatic Kanban Generation**
- `tasks.md` is the **canonical source of truth** for task graph generation.
- Prime compiles `tasks.md` into an active, machine-readable Kanban board (`.specify/kanban/board.json`).
- Each task becomes exactly one card containing:
  - `Card ID` (e.g. `TASK-001`)
  - `Title` & `Description`
  - `Dependencies` (Prerequisite Card IDs)
  - `Acceptance Criteria`
  - `Allowed File Scope`
  - `Status` (`TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`)

### **Phase 5 — Builder Dispatch**
- Prime dispatches **exactly one unblocked `TODO` card at a time** to Builder.
- Builder operates strictly within the assigned card boundary and allowed file scope.
- Builder **never receives direct user instructions** or un-scoped prompts.

### **Phase 6 — Auditor Verification**
- When Builder completes work, the card state moves to `IN_REVIEW`.
- Prime dispatches the `IN_REVIEW` card to Auditor.
- Auditor executes verification tests, cryptographic ledger verification (`verify-ledger`), and evidence validation (`audit-evidence`).
- If verification passes $\rightarrow$ Card transitions to `DONE`.
- If verification fails $\rightarrow$ Card transitions back to `TODO` with Auditor's failure trace context attached.

### **Phase 7 — Continuous Execution Loop**
- Prime loops through Phase 5 and Phase 6 automatically until 100% of Kanban cards reach `DONE`.

### **Phase 8 — Final Project Completion**
- Once all cards are `DONE`, Prime generates:
  - Final Evidence Report (`.specify/installation_report.json` / `.specify/update_report.json`)
  - Architectural Summary (`walkthrough.md`)
  - Test & Verification Summary
- Prime presents the completed project and evidence package to the User.

---

## 3. Communication & Governance Boundary Rules

1. **User Endpoint:** User communicates exclusively with Prime.
2. **Subagent Isolation:** Builder and Auditor operate as worker agents and never accept direct user prompts.
3. **No Code Before Spec:** Implementation work never starts before the SpecKit pipeline has completed and passed Prime Review Gate.
4. **Deterministic Audit Trail:** All state transitions and evidence submissions write hash-chained audit records to `.specify/memory/audit_log.jsonl`.
