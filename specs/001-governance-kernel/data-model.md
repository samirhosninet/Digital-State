# Data Model: Governance Kernel

## Entities

### 1. Agent Profile Registry (`AgentRegistry`)
Tracks participating agents, authorized roles, and verification details.
* **Fields**:
  * `agent_id`: String (UUID or unique handler name)
  * `designated_role`: Enum (`Prime`, `Builder`, `Auditor`, or custom role)
  * `public_key`: String (for credential verification)
  * `status`: Enum (`Active`, `Suspended`)
  * `registered_at`: ISO8601 DateTime

### 2. Lifecycle State (`LifecycleState`)
Represents the project governance state matching the Spec Kit workflow phases.
* **Fields**:
  * `feature_id`: String
  * `current_state`: Enum (`SPECIFICATION`, `PLANNING`, `TASKS`, `IMPLEMENTATION`, `VERIFICATION`, `COMPLETED`)
  * `last_transition_at`: ISO8601 DateTime
  * `updated_by_agent_id`: String

### 3. Verifiable Evidence (`VerifiableEvidence`)
Represents the audit records submitted at each gate.
* **Fields**:
  * `evidence_id`: String (UUID)
  * `feature_id`: String
  * `gate_type`: Enum (`SPECIFICATION`, `PLANNING`, `IMPLEMENTATION`, `VERIFICATION`)
  * `submitted_by`: String (Agent ID)
  * `evidence_content`: Metadata mapping
  * `signature`: String (proving identity of the submitter)
  * `status`: Enum (`Pending`, `Approved`, `Rejected`)
  * `reviewed_by`: String (Auditor Agent ID)

---

## State Transitions
```text
[SPECIFICATION] --(Prime sign-off)--> [PLANNING] --(Auditor plan sign-off)--> [IMPLEMENTATION] --(Auditor validation)--> [VERIFICATION] --(Prime approval)--> [COMPLETED]
```

* **Transition Rules**:
  1. From `SPECIFICATION` to `PLANNING`: Requires `Prime` verification.
  2. From `PLANNING` to `IMPLEMENTATION`: Requires `Builder` plan submittal and `Auditor` approval.
  3. From `IMPLEMENTATION` to `VERIFICATION`: Requires `Builder` implementation evidence log and `Auditor` sign-off.
  4. From `VERIFICATION` to `COMPLETED`: Requires `Prime` approval.
  5. Any unauthorized attempt reverts to block.
