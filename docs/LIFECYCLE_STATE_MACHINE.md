# LIFECYCLE STATE MACHINE — PRIME OPERATING MODEL

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Executive Summary

This document defines the formal **State Machine Specification** governing project lifecycle transitions within Digital State. The state machine maps high-level engineering phases directly to `GovernanceKernel` state tracking.

---

## 2. State Machine Diagram

```text
  ┌──────────────────┐
  │   IDLE / READY   │
  └────────┬─────────┘
           │ (User Prompt Received)
           ▼
  ┌──────────────────┐
  │ INTENT_ANALYSIS  │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐      (Artifact Inconsistency)
  │ SPECKIT_PIPELINE ├─────────────────────────────────────┐
  └────────┬─────────┘                                     │
           │                                               │
           ▼                                               │
  ┌──────────────────┐                                     │
  │ PRIME_REVIEW_GATE│◄────────────────────────────────────┘
  └────────┬─────────┘
           │ (Review Approved)
           ▼
  ┌──────────────────┐
  │ KANBAN_GENERATED │
  └────────┬─────────┘
           │
           ▼
┌──► BUILDER_DISPATCH ◄─────────────────────────┐
│          │ (Card Completed)                   │ (Verification Failed)
│          ▼                                    │
│    AUDITOR_REVIEW ────────────────────────────┘
│          │ (Verification Passed)
│          ▼
└─── CARD_DONE
           │ (All Cards DONE)
           ▼
  ┌──────────────────┐
  │ PROJECT_COMPLETE │
  └──────────────────┘
```

---

## 3. Formal State Transition Table

| Current State | Event / Trigger | Target State | Invariants & Governance Action |
| :--- | :--- | :--- | :--- |
| `IDLE` | User Prompt Received | `INTENT_ANALYSIS` | Prime parses prompt; checks requirement clarity. |
| `INTENT_ANALYSIS` | Clarification Needed | `CLARIFICATION_PROMPT` | Prime prompts user for missing requirements. |
| `INTENT_ANALYSIS` | Requirements Clear | `SPECKIT_PIPELINE` | Executes `specify` $\rightarrow$ `clarify` $\rightarrow$ `plan` $\rightarrow$ `checklist` $\rightarrow$ `tasks` $\rightarrow$ `analyze`. |
| `SPECKIT_PIPELINE` | SpecKit Execution Done | `PRIME_REVIEW_GATE` | Prime evaluates artifact suite consistency. |
| `PRIME_REVIEW_GATE` | Review Rejected | `SPECKIT_PIPELINE` | Auto-regenerates deficient design artifacts. |
| `PRIME_REVIEW_GATE` | Review Approved | `KANBAN_GENERATED` | Compiles `tasks.md` into `.specify/kanban/board.json`. |
| `KANBAN_GENERATED` | Dispatch Next Card | `BUILDER_DISPATCH` | Dispatches single unblocked card to Builder. |
| `BUILDER_DISPATCH` | Builder Card Finish | `AUDITOR_REVIEW` | Card transitions to `IN_REVIEW`. Auditor dispatched. |
| `AUDITOR_REVIEW` | Verification FAIL | `BUILDER_DISPATCH` | Card reset to `TODO` with failure log attached. |
| `AUDITOR_REVIEW` | Verification PASS | `CARD_DONE` | Card transitions to `DONE`. Hash log written. |
| `CARD_DONE` | Unblocked Cards Exist | `BUILDER_DISPATCH` | Dispatches next priority card to Builder. |
| `CARD_DONE` | 100% Cards DONE | `PROJECT_COMPLETE` | Prepares final evidence report and presents to User. |
