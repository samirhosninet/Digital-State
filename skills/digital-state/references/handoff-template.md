# Digital State Handoff Protocol Template

> Standardized format for all inter-agent handoffs in Digital State.

## Handoff Format

Every handoff message MUST follow this exact format:

```text
[FROM: <agent>] [TO: <agent>] [CARD: <card_id>]
Action: <VERB>
Summary: <what was done / what needs to happen>
Evidence: <raw logs, sources, command output — or N/A>
Acceptance Criteria: <list — or N/A>
Expected Evidence: <what the receiving agent should produce — or N/A>
File Boundaries: <if implementation, exact paths — or N/A>
Stop Condition: <when to stop>
```

## Valid Source-Target Pairs

| FROM | TO | Valid Actions |
|------|----|---------------|
| builder | prime | COMPLETE, BLOCK |
| auditor | prime | APPROVE, APPROVE WITH WARNINGS, REJECT, ESCALATE |
| prime | builder | EVIDENCE, IMPLEMENT |
| prime | auditor | AUDIT |

## Builder → Prime Handoff (Evidence Complete)

```text
[FROM: builder] [TO: prime] [CARD: t_xxxxxxxx]
Action: COMPLETE
Summary: Collected raw evidence for <task description>
Evidence: <attach full raw logs, command output, URLs>
Acceptance Criteria: <from the card>
Stop Condition: All evidence items collected
```

## Builder → Prime Handoff (Review Required — Phase B)

```text
[FROM: builder] [TO: prime] [CARD: t_xxxxxxxx]
Action: BLOCK
Summary: Implementation complete, review-required: <one-line evidence summary>
Evidence: <attach implementation diff, test output, file changes>
File Boundaries: <exact paths modified>
Stop Condition: Auditor issues APPROVE or APPROVE WITH WARNINGS
```

> **Note**: Builder MUST use `kanban_block(reason="review-required: ...")` — not `kanban_complete()` — for implementation cards requiring audit. Prime then promotes the same card to `status='review'` (Constitution Article XIV).

## Auditor → Prime Handoff (Approve)

```text
[FROM: auditor] [TO: prime] [CARD: t_xxxxxxxx]
Action: APPROVE
Summary: Evidence meets acceptance criteria. <any warnings>
Evidence: <auditor's own review notes, addenda>
```

## Auditor → Prime Handoff (Reject)

```text
[FROM: auditor] [TO: prime] [CARD: t_xxxxxxxx]
Action: REJECT
Summary: <precise failure details — what evidence is missing, what criteria unmet>
Evidence: <specific gaps observed>
```

## Validation Rules

1. `[FROM]` MUST be one of: builder, auditor, user
2. `[TO]` MUST be: prime
3. `[CARD]` MUST reference a valid board card
4. `Action` MUST be valid for the source agent
5. If validation fails, respond: `INVALID HANDOFF — Expected format: [FROM: agent] [TO: prime] [CARD: ID] Action: VERB`
