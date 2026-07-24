# ADR-005: PRIME OPERATING MODEL ARCHITECTURE & SINGLE-ENDPOINT ORCHESTRATION

**STATUS:** ACCEPTED  
**DATE:** 2026-07-24  
**DECISION-MAKERS:** Chief Software Architect, Prime Operating Model Architect  
**REPOSITORY:** `samirhosninet/Digital-State`  
**IMPACTED COMPONENT:** CLI Orchestration Layer & Governance Framework  

---

## 1. Context and Problem Statement

Following the `v1.16.0` release milestone, the low-level CLI commands (`install`, `update`, `doctor`, `version`, `uninstall`) reached feature completeness. However, end users were still required to manually invoke individual SpecKit workflow stages (`specify`, `plan`, `tasks`), dispatch Builder instructions, and prompt Auditor verification.

This manual workflow led to:
1. Inconsistent design artifact generation.
2. Un-analyzed task lists and skipped review gates.
3. Unsanctioned side-effects when users prompted Builder directly.
4. Fragmented audit logs across un-orchestrated agent interactions.

---

## 2. Decision Outcome

We decision to adopt the **Prime Operating Model** as the permanent, authoritative architectural operating system for Digital State.

### **Key Architectural Standards Adopted:**
1. **Single Entry Point:** Prime is the ONLY interface exposed to the user. User communicates exclusively with Prime.
2. **Automated SpecKit Pipeline:** Prime automatically executes the 6-stage SpecKit sequence (`specify` $\rightarrow$ `clarify` $\rightarrow$ `plan` $\rightarrow$ `checklist` $\rightarrow$ `tasks` $\rightarrow$ `analyze`) before any implementation begins.
3. **Prime Review Gate:** Prime reviews generated design artifacts and halts or regenerates deficient specs before code changes occur.
4. **Canonical Task Graph & Kanban:** `tasks.md` is compiled automatically into `.specify/kanban/board.json`.
5. **Sandboxed Worker Dispatch:** Builder receives exactly ONE unblocked Kanban task card at a time from Prime. Direct user prompting of Builder is strictly prohibited.
6. **Auditor Verification Gate:** Auditor verifies completed cards (`IN_REVIEW`) only. Passing cards move to `DONE`; failing cards revert to `TODO` with failure context attached.

---

## 3. Consequences

### **Positive Consequences:**
- **Zero-Touch Project Execution:** Users provide high-level goals; Prime orchestrates the entire engineering lifecycle automatically.
- **Strict Boundary Preservation:** Worker agents cannot edit frozen core paths (`src/digital_state/core/`, etc.).
- **Deterministic Evidence Generation:** Hash-chained audit logs under `.specify/memory/audit_log.jsonl` record all card transitions and verification verdicts.

### **Negative Consequences:**
- **No Direct Subagent Interactivity:** Users cannot bypass Prime to talk directly to Builder. All interaction must flow through Prime.

---

## 4. Compliance & Verification

Compliance is enforced by repository specifications:
- [`docs/PRIME_OPERATING_MODEL.md`](file:///d:/Digital-State/docs/PRIME_OPERATING_MODEL.md)
- [`docs/WORKFLOW_SPECIFICATION.md`](file:///d:/Digital-State/docs/WORKFLOW_SPECIFICATION.md)
- [`docs/PLANNING_ENGINE_SPECIFICATION.md`](file:///d:/Digital-State/docs/PLANNING_ENGINE_SPECIFICATION.md)
- [`docs/LIFECYCLE_STATE_MACHINE.md`](file:///d:/Digital-State/docs/LIFECYCLE_STATE_MACHINE.md)
- [`docs/FAILURE_AND_RECOVERY_POLICY.md`](file:///d:/Digital-State/docs/FAILURE_AND_RECOVERY_POLICY.md)
- [`docs/TASK_GRAPH_AND_KANBAN_SPECIFICATION.md`](file:///d:/Digital-State/docs/TASK_GRAPH_AND_KANBAN_SPECIFICATION.md)
- [`docs/AGENT_DISPATCH_AND_VERIFICATION_RULES.md`](file:///d:/Digital-State/docs/AGENT_DISPATCH_AND_VERIFICATION_RULES.md)
- [`docs/REPOSITORY_CONVENTION_RULES.md`](file:///d:/Digital-State/docs/REPOSITORY_CONVENTION_RULES.md)
