# Product Validation Remediation — Closure Evidence

**Event:** PRODUCT VALIDATION REMEDIATION (bounded, authorized)
**Authority:** PRIME (Governance) — executed by Builder, verified by Auditor
**Date:** 2026-07-17
**Branch:** `spec-012/authority-remediation`
**Scope:** BUG-VAL-001, BUG-VAL-002, BUG-VAL-003, BUG-VAL-004 + packaging / build / release artifacts / runtime fixes required by validated findings. No features, no architecture/ADR/spec changes.

---

## Acceptance Criteria — Verification Matrix

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | BUG-VAL-001 resolved | ✅ | `registry._permissions_for_role` lowercases; unit regression `test_bug_val_001_*` PASS; e2e auditor approval transitions state |
| 2 | BUG-VAL-002 resolved | ✅ | `--force` added to `register` CLI + `register_agent(force=)`; unit `test_bug_val_002_force_overwrites_existing` PASS |
| 3 | BUG-VAL-004 resolved | ✅ | Regenerated wheel `entry_points.txt` contains both `digitalstate` and `digital-state` (exact match to AC #7) |
| 4 | Current source builds | ✅ | `uv build` produces wheel + sdist with no errors |
| 5 | Fresh wheel generated | ✅ | `dist/digital_state-0.1.0-py3-none-any.whl` regenerated 2026-07-17 (post-fix) |
| 6 | Wheel metadata matches source | ✅ | Wheel embeds `digital_state/core/assets/{roles.json,trust_roots.json}`, both scripts; sdist includes `pyproject.toml` with both scripts and no `force-up` include |
| 7 | `entry_points.txt` contains `digitalstate` + `digital-state` | ✅ | Verified text: `[console_scripts]` `digital-state = digital_state.cli.cli:main` / `digitalstate = digital_state.cli.cli:main` |
| 8 | Clean installation succeeds | ✅ | Fresh venv `pip install dist/*.whl` → both launchers present, `doctor` overall_status=PASS |
| 9 | Both CLI launchers execute | ✅ | `digitalstate --help` and `digital-state --help` both run; full workflow executed via both |
| 10 | `digital-state doctor` returns PASS | ✅ | `overall_status = PASS` (installation/config/governance PASS) on clean install |
| 11 | End-to-end smoke test passes | ✅ | `scripts/smoke_e2e.py`: SPECIFICATION→COMPLETED, 5 transitions, Runtime-first identities |
| 12 | Regression suite passes | ✅ | `pytest`: **58 passed** (55 prior + 3 new BUG-VAL-001/002 regressions) |
| 13 | Release artifacts regenerated | ✅ | `dist/*.whl` + `dist/*.tar.gz` rebuilt from current source; verified contents |
| 14 | Product Validation evidence updated | ✅ | `VALIDATION-BUG-LOG.md` rewritten (all 4 resolved); this closure doc; INSTALLATION-VALIDATION + 03-VALUE-PROPOSITION tables updated |

---

## Files Changed (all map 1:1 to a validated defect)

| File | Change | Defect(s) |
|------|--------|-----------|
| `src/digital_state/core/registry.py` | `_permissions_for_role` lowercases key; `register_agent` gains `force=` overwrite | BUG-VAL-001, BUG-VAL-002 |
| `src/digital_state/cli/cli.py` | `register` gains `--force` flag; passed to `register_agent` + Runtime upsert | BUG-VAL-002 |
| `pyproject.toml` | Removed redundant `tool.hatch.build.targets.wheel.force-include` (duplicate include broke build) | BUG-VAL-003 |
| `tests/unit/test_bug_val_regressions.py` | New regression tests locking BUG-VAL-001 (case) + BUG-VAL-002 (`--force`) | AC #12 |
| `scripts/smoke_e2e.py` | New end-to-end lifecycle smoke test (Runtime-first identities, `--force` re-key) | AC #11 |
| `dist/digital_state-0.1.0-py3-none-any.whl` | Regenerated | BUG-VAL-003, BUG-VAL-004, AC #5–#7,#13 |
| `dist/digital_state-0.1.0.tar.gz` | Regenerated | AC #13 |
| `governance/product-validation/VALIDATION-BUG-LOG.md` | All 4 defects marked RESOLVED with fixes+evidence | AC #14 |
| `governance/product-validation/REMEDIATION-EVIDENCE.md` | This document | AC #14 |

No public APIs were changed. The `digital_state.cli.cli:main` entry target is unchanged;
only an additive `--force` argument was added to `register`. Architecture, governance model,
and ADRs are untouched.

---

## Reproduction (Auditor-independent)

```powershell
# 0. Clean, isolated environment (repo .venv is contaminated by Hermes PYTHONPATH;
#    use a fresh venv and unset PYTHONPATH so digital_state resolves to THIS repo)
uv venv --python 3.11 .venv-clean
$env:PYTHONPATH = ""
uv pip install --python .venv-clean/Scripts/python.exe -e .

# 1. Regression suite
.venv-clean/Scripts/python.exe -m pytest -q        # expect: 58 passed

# 2. Rebuild + verify release artifacts
uv build --python .venv-clean/Scripts/python.exe
python -c "import zipfile; z=zipfile.ZipFile('dist/digital_state-0.1.0-py3-none-any.whl'); print(z.read([n for n in z.namelist() if 'entry_points' in n][0]).decode())"
# -> [console_scripts] digital-state = ... ; digitalstate = ...

# 3. Clean-install validation
uv venv --python 3.11 .venv-install
uv pip install --python .venv-install/Scripts/python.exe dist/digital_state-0.1.0-py3-none-any.whl
.venv-install/Scripts/digitalstate doctor        # overall_status = PASS
.venv-install/Scripts/digital-state --help      # runs

# 4. End-to-end smoke (Runtime-first identities)
.venv-install/Scripts/python.exe scripts/smoke_e2e.py   # SPECIFICATION -> COMPLETED
```

---

## Residual (out of scope — requires independent human users)

The remediation closes all *code and packaging* defects that blocked a technical proxy from
completing the governance workflow. The following Product-Validation *human* gates remain open
and are explicitly NOT claimed resolved here (they require external, non-owner testers):

- Real human comprehension of the workflow.
- Willingness to pay / market validation.
- Cross-platform install by a non-owner (macOS/Linux).
- Time-to-complete by an unfamiliar user.
- Documentation clarity from a user's perspective.

**Verdict:** Product is restored to a releasable, externally installable, end-to-end functional
state. The four validated Product Validation defects are resolved and independently verified.
