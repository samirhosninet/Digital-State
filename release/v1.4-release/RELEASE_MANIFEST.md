# RELEASE MANIFEST — Digital State v1.4-release

| Field | Value |
|---|---|
| **Release Name** | Digital State v1.4-release |
| **Release State** | PRODUCTION RELEASE (FINAL PASS) |
| **Governance Event** | Release Finalization (PV-RELEASE-001) |
| **Commit SHA** | `4005834f3f0c3897f6585b60f8fd3a862a0f21ab` |
| **Commit Short** | `4005834` |
| **Tag** | `v1.4-release` (annotated, immutable) |
| **Tag Object SHA** | `76e90c9601896ac621f8454e26af433b10efe345` |
| **Tagger Date (UTC+3)** | `2026-07-18T01:00:42+03:00` |
| **Package Version** | `0.1.0` |
| **Wheel Artifact** | `digital_state-0.1.0-py3-none-any.whl` |
| **Wheel SHA256** | `c75d747930ef88d555a79cd9180e15a01d839b03af8d338cc0b63ea771948a1e` |
| **Build Timestamp (UTC)** | `2026-07-17T22:01:54Z` |
| **Reproducible Build** | YES — two independent `git archive v1.4-release` builds produced byte-identical wheels (identical SHA256). `SOURCE_DATE_EPOCH=1752796800` pinned for determinism. |
| **Python Version** | `3.11.15` (CPython, win32 / Windows x86_64) |
| **Hatchling Version** | build backend `hatchling` (resolved at build time via `uv build --wheel`); uv `0.11.29` |
| **Build Command** | `git archive v1.4-release \| tar -x` then `SOURCE_DATE_EPOCH=1752796800 uv build --wheel` |
| **Platform Compatibility** | py3-none-any (pure-Python, OS-independent). Requires `>=3.11`. Tested on Windows 10 / CPython 3.11.15. |
| **Git** | `git version 2.54.0.windows.1` |

---

## Test Summary

- **pytest:** `58/58 PASS` (full suite, uv run pytest 9.1.1)
- Includes regression locks: `tests/unit/test_bug_val_regressions.py` (BUG-VAL-001, BUG-VAL-002)
- Pre-release classification: the single known failure from the acceptance audit window was classified as test-harness/environmental, not a shipping blocker, and is now GREEN (58/58).

## Doctor Summary

`digitalstate doctor` → **overall_status: PASS**

| Subsystem | Status |
|---|---|
| installation | PASS (Python 3.11.15, cryptography 46.0.7) |
| configuration | PASS (.specify present, all files) |
| governance | PASS (state readable) |
| hermes | PASS (LIVE adapter, self_test PASS, adapter_ready) |

## Acceptance Audit (prior gate)

- VAL-001: CLOSED
- VAL-002: CLOSED
- VAL-003: CLOSED
- VAL-004: CLOSED
- Independent Acceptance Audit: CONDITIONAL PASS (remaining conditions governance/process only) → satisfied by this release finalization.

---

## Artifact Inventory

```
release/v1.4-release/
├── RELEASE_MANIFEST.md                         (this file)
├── RELEASE_BUNDLE_README.md                    (bundle contents index)
└── dist/
    ├── digital_state-0.1.0-py3-none-any.whl    SHA256 c75d7479…948a1e
    └── digital_state-0.1.0-py3-none-any.whl.sha256
```

Source remediation artifacts (committed with `4005834`, tracked in git):
- `src/digital_state/core/registry.py` — BUG-VAL-001 (role-case normalization), BUG-VAL-002 (`--force` re-register)
- `src/digital_state/cli/cli.py` — `--force` CLI flag
- `pyproject.toml` — drop redundant hatchling force-include
- `tests/unit/test_bug_val_regressions.py` — regression locks
- `scripts/smoke_e2e.py` — end-to-end governance lifecycle smoke test
- `governance/product-validation/` — Product Validation investigation + remediation evidence

**Excluded from release (per directive step 2):**
- `.audit-clean/`, `.audit-venv/`, `.venv-install/` — temporary audit/install environments (not part of the package).
- `governance/product-validation/test-keys/*.pem` — private keys, excluded by `.gitignore` (`*.pem`); never committed.

---

## Immutable State Declaration

- Release commit `4005834f…` is the immutable source artifact.
- Tag `v1.4-release` is annotated and MUST NOT be renamed or rewritten after publication.
- Any required post-release source change spawns a NEW release tag, not a mutation of `v1.4-release`.

**Governance State Transition:** CONDITIONAL PASS → **FINAL PASS / PRODUCTION RELEASE / RELEASE APPROVED**
