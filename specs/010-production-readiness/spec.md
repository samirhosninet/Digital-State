# Spec 010 — Digital-State Production Readiness

## Purpose
Bring the repository to a production-ready state by resolving the multi-layer regression introduced by
spec 009 (production-trust-hardening), then obtaining an independent Auditor sign-off before any push.

## Governance Event
- **Event:** "Digital-State Production Readiness"
- **Opened by:** PRIME (Kanban Orchestrator)
- **Trigger:** Pre-push gate found 17 failing tests + private-key leakage risk (contained).
- **Mode:** BACKLOG → READY → IN PROGRESS → REVIEW → DONE, repeated until Auditor issues final decision.

## Current State (fresh repository evidence, captured this session)
- HEAD: `931c7ef` (branch `main`, up to date with `origin/main`)
- Test runner: `uv run pytest` (project `pyproject.toml`, uv)
- Investigation start: **17 failing tests**, root-caused to 6 independent causes (RC-1..RC-6).
- Remediation pass P0–P2 completed RC-1, RC-3, RC-2, RC-3b, RC-5.
- Remaining open: **RC-4a, RC-4b, RC-6**.
- Security: private keys (`.specify/keys/*.pem`) are git-ignored (`*.pem`, `.specify/keys/`, `scratch/`
  added to `.gitignore`). No secrets are staged.

## Acceptance Criteria (production gate)
1. `uv run pytest` exits **0** (all tests pass).
2. No private keys / secrets in any staged or committed file (`git status` + `.gitignore` verify).
3. Every RC closed with repository-backed evidence (modified files, tests executed, commit hash).
4. Auditor independently verifies each Builder task before DONE.
5. Auditor issues the final production decision (push authorized only after sign-off).

## Out of Scope
- No `git push` to `origin` until Auditor signs off.
- No rollback of spec 009's trust model (ECDSA P-256, independent approval) without explicit PRIME decree.

## Architectural Decision — RC-6 (PRIME decree)
**Option 1 adopted:** align the story tests with the submit/approve separation introduced by spec 009.
The production trust model (independent approval, no implicit self-approval) is preserved. Any agent may
*submit* evidence; only an independent approver holding the relevant `approve_*` permission (e.g.
`auditor-agent` holding `approve_spec`) may transition a gate. The prior expectation that `builder-agent`
is rejected at *submit* time is obsolete; the correct invariant is "builder may submit, builder may not
self-approve."
