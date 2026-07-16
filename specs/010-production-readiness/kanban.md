# Kanban Board — Digital-State Production Readiness

Columns: BACKLOG → READY → IN PROGRESS → REVIEW → DONE

## Cards
| ID | Title | RC | Owner | Status | Depends |
|----|-------|----|-------|--------|---------|
| K-01 | Registry bootstrap: restore baseline trust roots | RC-1 | Builder | DONE | — |
| K-02 | Lifecycle contract: align `approve_spec` permission | RC-3 | Builder | DONE | K-01 |
| K-03 | Cryptographic verification: real ECDSA signing in tests | RC-2, RC-3b | Builder | DONE | K-01 |
| K-04 | Restore independent SPECIFICATION approval (auto-approve removed) | RC-5 | Builder | DONE | K-02, K-03 |
| K-05 | Align story tests with submit/approve separation | RC-6 | Builder | DONE | K-04 |
| K-06 | CLI `register`: align tests to `--public-key-file`/`--key-id` | RC-4a | Builder | DONE | K-04 |
| K-07 | Plugin hook: emit real `agent_key` ECDSA identity | RC-4b | Builder | DONE | K-04 |
| K-08 | Full test-suite green run + regression confirmation | — | Builder | DONE (53 passed ✅) | K-05, K-06, K-07 |
| A-01 | Audit K-01..K-04 evidence (files + tests + commit) | — | Auditor | DONE (10/10 related tests pass ✅) | K-04 |
| A-02 | Audit K-05..K-07 (RC-6, RC-4a, RC-4b) | — | Auditor | DONE (53 passed, 0 secrets staged ✅) | K-08 |
| A-03 | Final production decision (push authorized?) | — | Auditor | IN PROGRESS | A-01, A-02 |

## Task DAG (dependency order)
```
K-01 ─┬─► K-02 ─► K-04 ─┬─► K-05 ─┐
     └─► K-03 ──────────┘─► K-06 ─┤
                                 └─► K-07 ─► K-08 ─► A-02 ─► A-03
                                                (A-01 runs in parallel over K-01..K-04)
```

## Builder Assignments
- K-01, K-02, K-03, K-04 — DONE (evidence in this session's diffs).
- K-05: update `test_story1.py` / `test_story2.py` so builder submit is allowed, independent auditor
  approval enforced; fix log-count assertions (3→2, 6→4) accordingly.
- K-06: decide CLI compatibility — prefer updating `test_cli_flow` to `--public-key-file` + `--key-id`
  (matches spec 009 intent) OR restoring `--key`. Recommend: update tests to new contract.
- K-07: update `test_hermes_flow` to pass a real ECDSA `agent_key` dict instead of a plaintext string.

## Auditor Assignments
- A-01: independently verify K-01..K-04 — confirm `uv run pytest` subset passes, inspect diffs, confirm
  no private keys staged (`git diff --cached --stat`, `.gitignore`).
- A-02: independently verify K-05..K-07 after K-08 green run.
- A-03: issue final production decision only when all tests pass and no secrets are staged.

## Governance Rules (PRIME)
- PRIME never writes production code.
- PRIME never skips Auditor.
- No assumptions; every conclusion backed by fresh repository evidence.
- Builder task → REVIEW only after repository-backed evidence (files, tests, commit hash).
- Auditor verifies before DONE. Loop until A-03.
