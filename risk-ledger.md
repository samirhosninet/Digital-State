# Risk Ledger — Digital State

> Canonical store for risk entries, suppressions, and risk-acceptance sign-offs.
> Managed per `skills/premortem-plus/SKILL.md` requirements.

| ID | Description | Severity | Status | Owner | Date | Review |
|----|-------------|----------|--------|-------|------|--------|
| RISK-001 | No CLI command for `blocked → review` promotion; requires direct DB write | High | Mitigated | Prime | 2026-06-24 | Script `scripts/promote-to-review.sh` provides CLI wrapper; full Hermes enhancement tracked as follow-up |
| RISK-002 | `install.ps1` `Get-RootModelConfig` function has quoting error on line 60 | High | Closed | Builder | 2026-06-24 | Fixed: `.Trim('"', "'")` → `.Trim([char]34, [char]39)` in install.ps1 line 60 |
| RISK-003 | 9 pre-existing `validate-final.ps1` errors predating current work | Medium | Open | Builder | 2026-06-23 | Track separately |
| RISK-004 | Cross-model same-family audit verdict cap (nvidia family) | Low | Acceptable | Auditor | 2026-06-23 | Inert — same provider family |
| RISK-005 | Phantom hook names in YAML comments (`pre_chat`, `post_chat`) — inert but confusing | Low | Suppress | Auditor | 2026-06-23 | Comments only, not executed |
| RISK-006 | Model provider hardcoded in portable config.yaml files — violates overlay portability | Medium | Closed | Prime | 2026-06-24 | Fixed in Phase 10 T081: model/provider removed from config.yaml; installer sets at install time |
| RISK-007 | No automated test suite — governance cycle and installer rely on manual verification | High | Closed | Prime | 2026-06-24 | Phase 10 T083: pytest suite added (59 tests, 57 pass out of box, 2 config-only fixes) |

## Suppressions

| RISK ID | Reason | Authorized By | Date |
|---------|--------|---------------|------|
| RISK-005 | Inert YAML comments; retained for fix-history documentation | Auditor | 2026-06-23 |

## Risk Acceptance Sign-offs

| RISK ID | Decision | Rationale | Sign-off By | Date |
|---------|----------|-----------|-------------|------|
| RISK-004 | Accept | Same-family models share provider infrastructure; no cross-provider audit gap | Auditor | 2026-06-23 |

## Closure Records

| RISK ID | Closed Date | Resolution | Evidence |
|---------|-------------|------------|----------|
| RISK-002 | 2026-06-24 | Fixed in install.ps1 line 60 | `.Trim([char]34, [char]39)` replaces old `.Trim('"', "'")`; validator passes |

## Mitigation Records

| RISK ID | Mitigated Date | Mitigation | Remaining Gap |
|---------|----------------|------------|---------------|
| RISK-001 | 2026-06-24 | `scripts/promote-to-review.sh` wraps direct DB write into CLI command; Prime or operator can run `bash scripts/promote-to-review.sh <card_id>` instead of raw SQL | No native `hermes kanban promote` subcommand yet; depends on kanban.db path resolution |
