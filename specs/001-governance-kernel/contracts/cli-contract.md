# Interface Contract: CLI Command Schema

This contract defines the technology-agnostic command line interface (CLI) exposed by the Digital State governance kernel.

## Commands

### 1. Agent Registration
Registers a new agent profile and binds it to a designated governance role.
* **Syntax**: `digitalstate register --id <agent_id> --role <role> --key <key>`
* **Arguments**:
  * `--id`: Unique identifier for the agent
  * `--role`: Assigned governance profile (`Prime`, `Builder`, `Auditor` or custom role)
  * `--key`: Verification credential for signing transactions

### 2. Status Inspection
Retrieves the current state and transition history of a feature.
* **Syntax**: `digitalstate status --feature <feature_id>`
* **Output**: Structured JSON containing:
  * `feature_id`
  * `current_state` (one of `SPECIFICATION`, `PLANNING`, `TASKS`, `IMPLEMENTATION`, `VERIFICATION`, `COMPLETED`)
  * `history` (array of transitions, including timestamps and agent IDs)

### 3. Evidence Submission
Submits verifiable evidence to request a transition to the next phase.
* **Syntax**: `digitalstate submit --feature <feature_id> --gate <gate> --evidence <evidence_metadata> --agent <agent_id>`
* **Arguments**:
  * `--gate`: Target checkpoint gate (`SPECIFICATION`, `PLANNING`, `IMPLEMENTATION`, `VERIFICATION`)
  * `--evidence`: Context data representing completed phase achievements
  * `--agent`: Submitting agent ID

### 4. Gate Auditing (Approve / Reject)
Audits a pending transition request. Only authorized auditor or prime roles can execute this.
* **Syntax**:
  * **Approve**: `digitalstate approve --feature <feature_id> --gate <gate> --agent <agent_id>`
  * **Reject**: `digitalstate reject --feature <feature_id> --gate <gate> --reason <reason> --agent <agent_id>`
