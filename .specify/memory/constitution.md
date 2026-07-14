<!--
Sync Impact Report:
- Version change: v1.1.0 → v1.2.0
- List of modified principles:
  - PRINCIPLE_1: "I. Separation of Governance and Execution" (Unchanged).
  - PRINCIPLE_2: "II. Role Segregation" (Unchanged).
  - PRINCIPLE_3: "III. Immutable Accountability" (Unchanged).
  - PRINCIPLE_4: "IV. Gate-Based Progression" (Unchanged).
  - PRINCIPLE_5: "V. Independent Verification" (Unchanged).
- Added sections: None.
- Removed sections: "Workflow & Quality Gates".
- Modified constraints:
  - Role Registration → Verifiable Identity: Replaced registry-specific constraint with a principle requiring verifiable identity and authorized role context.
- Modified governance:
  - Amendments: Replaced profile-specific voting with generalized consensus ratification across designated stakeholder roles.
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ Verified aligned)
  - .specify/templates/spec-template.md (✅ Verified aligned)
  - .specify/templates/tasks-template.md (✅ Verified aligned)
- Follow-up TODOs: None (all placeholders resolved)
-->

# Digital State Constitution

## Core Principles

### I. Separation of Governance and Execution
The boundary between governance and execution is absolute:
* **Digital State** governs all policy, compliance, registration, and lifecycle constraints.
* **Hermes Agent** executes all actions, tasks, and code loops.
The governance layer must never perform execution tasks, and the execution layer must never override governance rules.

### II. Role Segregation
The governance system defines and enforces three distinct, segregated agent profiles:
* **Prime**: Responsible for defining goals, formulating requirements, and verifying final outcomes.
* **Builder**: Responsible for designing technical implementation plans and executing development work.
* **Auditor**: Responsible for independent quality checks, compliance verification, and gate monitoring.
An agent profile must never execute actions or assume responsibilities designated for a different profile.

### III. Immutable Accountability
All agent actions, state transitions, and registry records must be documented in a permanent, auditable log. No lifecycle transition or execution authorization is valid without a corresponding verified log entry.

### IV. Gate-Based Progression
Every phase of the development lifecycle must pass through explicit, independent check gates. Progression to a subsequent stage is prohibited until the preceding gate's criteria have been fully satisfied.

### V. Independent Verification
Verification of compliance, quality, and correctness must be executed independently of implementation. No agent profile may self-verify, approve, or authorize their own work. The Auditor profile has independent veto authority over all compliance gates.

## Core Constraints

1. **Verifiable Identity**: Every participating agent must possess a verifiable identity and an authorized role context before executing or validating actions within the lifecycle.
2. **Audit Trails**: All system states must remain verifiable, trace-complete, and open to retrospective auditing.

## Governance

1. **Amendments**: Amendments to this Constitution require consensus ratification across all designated stakeholder roles defined within the governance layer.
2. **Versioning Policy**: Semantic versioning is applied: Major bumps represent changes to core non-negotiable principles, Minor bumps represent additions of new principles/constraints, and Patch bumps represent text clarifications.

**Version**: 1.2.0 | **Ratified**: 2026-07-14 | **Last Amended**: 2026-07-14
