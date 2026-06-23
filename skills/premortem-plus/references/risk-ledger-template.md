# Risk Ledger Template

> Per `skills/premortem-plus/SKILL.md` — every triggered risk MUST have an entry in the target project's `risk-ledger.md`.

## Risk Entries Table

| ID | Description | Severity | Status | Owner | Date | Review |
|----|-------------|----------|--------|-------|------|--------|
| RISK-001 | <one-line description> | High / Medium / Low | Open / Mitigated / Acceptable / Suppress | <agent or operator> | YYYY-MM-DD | <next action> |

## Suppressions Table

| RISK ID | Reason | Authorized By | Date |
|---------|--------|---------------|------|
| | | | |

## Risk Acceptance Sign-offs Table

| RISK ID | Decision | Rationale | Sign-off By | Date |
|---------|----------|-----------|-------------|------|
| | | | | |

## Rules

- **Severity**: High = blocks progress until mitigated; Medium = must be tracked and reviewed; Low = may be accepted or suppressed with documented rationale.
- **Status → Open**: Active risk requiring action.
- **Status → Mitigated**: Control implemented; residual risk acceptable.
- **Status → Acceptable**: Risk accepted without mitigation (sign-off required).
- **Status → Suppress**: Low-severity inert risk (suppression reason required).
- **Canonical store**: `risk-ledger.md` is the risk-of-record. Kanban comments and handoffs may reference it but cannot replace it.
