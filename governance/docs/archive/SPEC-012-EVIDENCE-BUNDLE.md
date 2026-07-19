# SPEC-012 — Evidence Bundle (attach to PR)

**Branch:** `spec-012/authority-remediation`
**Commit:** `f55838c387fb3dedb8ea987a8bc922bb9f34d181`
**Status:** AUDITOR PASS · COMMIT + PUSH done · PR pending UI opening

---

## A. Test results — 55 passed, 0 failed

```
$ git checkout spec-012/authority-remediation
$ python -m pytest -p no:cacheprovider
55 passed in 85.69s (0:01:25)
```

Command: `python -m pytest -p no:cacheprovider`
Expected output: `55 passed`

## B. Runtime Authority divergence proof

```
$ PYTHONPATH=src python audit_divergence_proof.py
Runtime key    == Engine resolved key        (A == A)
Workspace key  != Engine resolved key        (B != A)
Signature(A-private) -> PASS
Signature(B-private) -> FAIL
=> EFFECTIVE AUTHORITY: RUNTIME (A)
exit 0
```

## C. Authority-divergence test (unit)

`tests/unit/test_runtime_identity_resolution.py`:
- `test_runtime_authority_overrides_workspace` — Runtime key A wins over
  workspace key B; B-signed payload FAILs. (PASS)
- `test_get_agent_falls_back_to_workspace_when_runtime_empty` — fallback guard. (PASS)

## D. Files committed (single scoped commit)

```
src/digital_state/core/registry.py          Runtime-first get_agent
src/digital_state/cli/cli.py                deterministic trust-root registration
src/digital_state/runtime/                  Runtime subsystem (stores/store/provision/manifest)
src/digital_state/core/assets/              trust_roots.json + roles.json + profiles
.specify/agents.json                        sign_off_spec -> approve_spec
pyproject.toml                             digital-state alias + assets force-include
tests/unit/test_cli_commands.py             workspace-not-authoritative assertions
tests/unit/test_runtime_identity_resolution.py  authority-divergence test
tests/conftest.py                           per-test DIGITAL_STATE_HOME isolation
tests/integration/test_installation.py     Windows-path isolation fix
audit_divergence_proof.py                   independent divergence proof
```

## E. Restrictions honored

- No ADR / IA modification.
- No architectural change, no feature expansion.
- No secrets (private keys git-ignored under `.specify/keys/`).
- Unrelated `specs/010-production-readiness/kanban.md` change deliberately excluded.
