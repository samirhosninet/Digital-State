# Risk Ledger — Digital State

> Canonical store for risk entries, suppressions, and risk-acceptance sign-offs.
> Managed per `skills/premortem-plus/SKILL.md` requirements.

| ID | Description | Severity | Status | Owner | Date | Review |
|----|-------------|----------|--------|-------|------|--------|
| RISK-001 | No CLI command for `blocked → review` promotion; requires direct DB write | High | Open | Prime | 2026-06-23 | Pending Hermes enhancement |
| RISK-002 | `install.ps1` `Get-RootModelConfig` function has quoting error on line 60 | High | Open | Builder | 2026-06-23 | Needs PowerShell escape fix |
| RISK-003 | 9 pre-existing `validate-final.ps1` errors predating current work | Medium | Open | Builder | 2026-06-23 | Track separately |
| RISK-004 | Cross-model same-family audit verdict cap (nvidia family) | Low | Acceptable | Auditor | 2026-06-23 | Inert — same provider family |
| RISK-005 | Phantom hook names in YAML comments (`pre_chat`, `post_chat`) — inert but confusing | Low | Suppress | Auditor | 2026-06-23 | Comments only, not executed |

## Suppressions

| RISK ID | Reason | Authorized By | Date |
|---------|--------|---------------|------|
| RISK-005 | Inert YAML comments; retained for fix-history documentation | Auditor | 2026-06-23 |

## Risk Acceptance Sign-offs

| RISK ID | Decision | Rationale | Sign-off By | Date |
|---------|----------|-----------|-------------|------|
| RISK-004 | Accept | Same-family models share provider infrastructure; no cross-provider audit gap | Auditor | 2026-06-23 |
