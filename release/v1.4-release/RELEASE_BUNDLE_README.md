# FINAL RELEASE BUNDLE — Digital State v1.4-release

This directory is the immutable **FINAL RELEASE BUNDLE** for the SPEC-012
Runtime-first identity authority remediation (Product Validation closing fixes
BUG-VAL-001 / BUG-VAL-002). It is the authoritative evidence package for the
governance transition to **PRODUCTION RELEASE**.

## Contents

| File | Purpose |
|---|---|
| `RELEASE_MANIFEST.md` | Human-readable release manifest (commit SHA, tag, wheel SHA256, build timestamp, Python/hatchling versions, test & doctor summaries, platform compatibility, artifact inventory, excluded items, immutable-state declaration). |
| `release-evidence.json` | Machine-readable evidence record (same facts, generated from git/toolchain — single source of truth). |
| `dist/digital_state-0.1.0-py3-none-any.whl` | The reproducible release wheel built from tag `v1.4-release`. |
| `dist/digital_state-0.1.0-py3-none-any.whl.sha256` | Detached SHA256 checksum (verify with `sha256sum -c`). |

## Verification (reproducible by any auditor)

```bash
# 1. Checksum
sha256sum -c release/v1.4-release/dist/digital_state-0.1.0-py3-none-any.whl.sha256
#    -> digital_state-0.1.0-py3-none-any.whl: OK

# 2. Reproduce the wheel from the immutable tag
rm -rf /tmp/ds && mkdir -p /tmp/ds
git archive v1.4-release | tar -x -C /tmp/ds
(cd /tmp/ds && SOURCE_DATE_EPOCH=1752796800 uv build --wheel)
sha256sum /tmp/ds/dist/digital_state-0.1.0-py3-none-any.whl
#    -> c75d747930ef88d555a79cd9180e15a01d839b03af8d338cc0b63ea771948a1e

# 3. Confirm the tag points at the release commit
git rev-list -n1 v1.4-release   # 4005834f3f0c3897f6585b60f8fd3a862a0f21ab
```

## Acceptance Criteria — FINAL RELEASE

- [x] Release commit exists (`4005834…`)
- [x] Immutable annotated Git tag exists (`v1.4-release`)
- [x] Release artifacts reproducible (identical SHA256 across two builds)
- [x] Release Manifest generated (`RELEASE_MANIFEST.md`)
- [x] Release Bundle archived (this directory)
- [x] Repository reaches immutable Production Release state

**Governance State:** CONDITIONAL PASS → **FINAL PASS / PRODUCTION RELEASE / RELEASE APPROVED**

## Freeze Notice

This bundle is **frozen**. The release tag `v1.4-release` MUST NOT be renamed or
rewritten. Any required post-release source modification spawns a NEW release
tag, not a mutation of this one.
