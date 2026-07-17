# SPEC-012 — FINAL REMEDIATION Re-Audit Package

**Prepared for:** AUDITOR FINAL VERIFICATION
**Status:** BUILDER → AUDITOR FINAL VERIFICATION → COMMIT AUTHORIZATION
**No ADR / IA modification. No commit. No push.**

---

## 1. Acceptance of the authority invariant

The Runtime-first identity resolution invariant (CRITICAL-01/02/03 from the
prior cycle) is **preserved and unchanged** in this final cycle:

- `AgentRegistry.get_agent` still queries the Runtime IdentityStore FIRST and
  the workspace registry only as a fallback (when the Runtime is unavailable or
  lacks the identity). No code path returns a workspace identity while a Runtime
  identity for the same id exists.
- `audit_divergence_proof.py` still exits 0 with `EFFECTIVE AUTHORITY: RUNTIME (A)`.
- `tests/unit/test_runtime_identity_resolution.py` (the authority-divergence
  test, X/A/B scenario) still passes.

No engine code changed this cycle beyond what was already accepted.

---

## 2. Blocker resolution — complete suite green with zero failures

### Blocker 1: the three (and all) failing pre-existing tests are resolved

The prior full-suite run showed 14 red tests. Independent isolation testing
(each test run alone in a fresh process with its own `DIGITAL_STATE_HOME`)
proved **13 of those 14 were NOT genuine failures** — they were **cross-test
`DIGITAL_STATE_HOME` pollution**: the previous remediation never isolated the
Runtime per test, so the first test that provisioned the *shared* default
Runtime (`LOCALAPPDATA/digital-state`) changed identity resolution for every
later test that relied on the workspace store. The remaining 1
(`test_end_to_end_installation`) was a genuine pre-existing **Windows-path bug**
in the test itself (it pointed the subprocess `init` at a git-bash `/tmp` path
that resolves inconsistently on Windows).

**Fixes (test-hygiene only — no engine change, no authority regression):**

1. `tests/conftest.py` — added an **autouse `isolate_runtime_home` fixture**
   that gives every test a private, empty Runtime root (real Windows path via
   pytest `tmp_path`) by setting `DIGITAL_STATE_HOME`. This eliminates the
   cross-test pollution deterministically and makes `get_agent` fall back to the
   workspace registry unless a test provisions its own Runtime. Runtime-first
   authority is preserved: a test that bootstraps the Runtime still wins.

2. `tests/integration/test_installation.py` — the subprocess `init`/`doctor`
   steps now **inherit the fixture-isolated `DIGITAL_STATE_HOME`** instead of
   overriding it with `os.path.join(dest_root, ".ds-runtime")` (a git-bash
   `/tmp` path). The parent's manifest check reads the same isolated root the
   subprocess used. This removes the Windows path-resolution bug.

### Blocker 2: independently reproducible evidence — zero failures

Two consecutive full-suite runs (no shell `DIGITAL_STATE_HOME` override;
relying solely on the autouse fixture):

```
$ python -m pytest -p no:cacheprovider
RUN 1: 55 passed in 79.72s
RUN 2: 55 passed
```

Plus the SPEC-012 deliverables, independently:

```
$ python -m pytest tests/unit/test_runtime_identity_resolution.py
..  (authority-divergence test + workspace-fallback guard) — 2 passed

$ PYTHONPATH=src python audit_divergence_proof.py ; echo $?
EFFECTIVE AUTHORITY: RUNTIME (A)
0
```

**Result: 55 passed, 0 failed, 0 errors, exit code 0 — reproducible.**

### Blocker 3: scope of modified files

This final cycle modified **only test files** (test-hygiene):

| File | Change | Scope |
|------|--------|-------|
| `tests/conftest.py` | +24 lines: autouse `isolate_runtime_home` fixture | In scope — required to make the accepted authority fix reproducibly green (resolves the pollution failures). No engine change. |
| `tests/integration/test_installation.py` | Subprocess inherits the isolated `DIGITAL_STATE_HOME` instead of a git-bash `/tmp` override | In scope — fixes the one genuine pre-existing Windows-path test bug; no identity logic touched. |

All other working-tree changes (`src/digital_state/core/registry.py`,
`src/digital_state/cli/cli.py`, `src/digital_state/runtime/`,
`src/digital_state/core/assets/`, `tests/unit/test_cli_commands.py`,
`tests/unit/test_runtime_identity_resolution.py`, `audit_divergence_proof.py`,
`.specify/agents.json`, `pyproject.toml`, `kanban.md`) are the accepted
SPEC-012 remediation from the prior cycle (authority fix, required Runtime/assets
support, authority-divergence test, proof). No ADR/IA was modified. No commit,
no push.

No modified file exceeds the approved implementation scope: the engine change
(`get_agent` order) was already accepted, and this cycle's changes are confined
to test infrastructure necessary to prove the suite green without regressing
Runtime authority.

---

## 3. Deliverables checklist

- [x] Runtime-first identity resolution preserved
- [x] Runtime authority preserved
- [x] All pre-existing failing tests resolved (1 genuine Windows-path bug fixed; 13 pollution failures eliminated by per-test Runtime isolation)
- [x] Complete suite: 55 passed, 0 failed, reproducible (RUN 1 + RUN 2)
- [x] Authority-divergence test + independent proof still green
- [x] Modified files within approved scope (test-hygiene only)
- [x] No ADR / IA modification
- [x] No commit / No push

---

## 4. Reproduction (auditor)

```bash
# Full suite — expect "55 passed", exit 0 (reproducible)
python -m pytest -p no:cacheprovider

# SPEC-012 authority test
python -m pytest tests/unit/test_runtime_identity_resolution.py -v

# Independent authority divergence proof
PYTHONPATH=src python audit_divergence_proof.py
# expected: EFFECTIVE AUTHORITY: RUNTIME (A), exit 0
```
