# AGENT DISPATCH AND VERIFICATION RULES — BUILDER & AUDITOR CONTRACTS

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Prime Orchestration Engine  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Executive Summary

This specification establishes the mandatory execution, isolation, and verification rules for worker agents (**Builder** and **Auditor**) dispatched by **Prime**.

---

## 2. Builder Dispatch & Execution Rules

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        BUILDER BOUNDARY RULES                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Builder receives instructions EXCLUSIVELY via Prime Kanban Dispatch. │
│ 2. Builder NEVER communicates directly with the User.                  │
│ 3. Builder MUST NOT edit files outside allowed_file_scope.             │
│ 4. Builder MUST NOT modify frozen core directories:                    │
│    • src/digital_state/core/                                           │
│    • src/digital_state/hermes/                                         │
│    • src/digital_state/bootstrap/                                      │
│    • src/digital_state/sdk/                                            │
│    • src/digital_state/observability/                                  │
│ 5. Upon completion, Builder transitions Card status to IN_REVIEW.      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Auditor Verification Rules

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        AUDITOR VERIFICATION RULES                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Auditor verifies ONLY cards with status IN_REVIEW.                  │
│ 2. Auditor NEVER communicates directly with the User.                  │
│ 3. Auditor MUST execute mandatory verification suite:                  │
│    a. Run pytest on affected test modules.                             │
│    b. Execute digitalstate verify-ledger.                              │
│    c. Execute digitalstate audit-evidence.                             │
│ 4. If all checks PASS ──► Card status transitions to DONE.              │
│ 5. If any check FAILS ──► Card status transitions to TODO with failure │
│    report logged in .specify/kanban/failures/.                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Prime Gateway Proxy Contract

All agent communications are proxied strictly through Prime:

- **User Direct Prompts to Builder / Auditor:** Intercepted and rejected with error:
  `"Access Denied: Worker agents operate strictly under Prime orchestration. Please submit your request to Prime."`
- **Subagent Status Reporting:** Subagents report progress, output logs, and completion status to Prime. Prime synthesizes and formats natural language updates for the User.
